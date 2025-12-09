"""
Enerji Tüketim Tahmin Modülü
Machine Learning kullanarak gelecek tüketim ve maliyet tahminleri yapar.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, mean_absolute_percentage_error
from sklearn.preprocessing import StandardScaler
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Dict
import warnings
warnings.filterwarnings('ignore')

# XGBoost import (opsiyonel - yüklü değilse random forest kullanır)
try:
    from xgboost import XGBRegressor  # type: ignore
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("[UYARI] XGBoost yüklü değil. 'pip install xgboost' ile yükleyebilirsiniz.")

# LightGBM import (opsiyonel)
try:
    from lightgbm import LGBMRegressor  # type: ignore
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    print("[UYARI] LightGBM yüklü değil. 'pip install lightgbm' ile yükleyebilirsiniz.")


class EnergyPredictor:
    """
    Enerji tüketimi ve maliyetini tahmin eden machine learning sınıfı.
    Random Forest modeli kullanarak yüksek doğrulukta gelecek tahminleri yapar.
    """
    
    def __init__(self):
        """Tahmin modelini başlat - Random Forest kullanır"""
        self.consumption_model = None  # Random Forest olacak
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = []
        self.avg_unit_price = 6.34
        self.category_distribution = {}
        self.min_date = None
        self.reference_year = None
        self.reference_month = None
        self.best_model_name = "Random Forest"
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tahmin için gerekli özellikleri (features) hazırla
        
        Args:
            df: İşlenmiş veri DataFrame'i
            
        Returns:
            Özellikler eklenmiş DataFrame
        """
        df = df.copy()
        
        # Tarih özelliklerini ekle
        if 'term_date' in df.columns:
            df['year'] = df['term_date'].dt.year  # type: ignore
            df['month'] = df['term_date'].dt.month  # type: ignore
            df['quarter'] = df['term_date'].dt.quarter  # type: ignore
        
        # Zaman serisi özellikleri - kaç ay geçtiğini hesapla
        if 'term_date' in df.columns:
            min_date = df['term_date'].min()
            # Referans tarihini sakla (tahmin sırasında kullanılacak)
            if self.min_date is None:
                self.min_date = min_date
                self.reference_year = min_date.year
                self.reference_month = min_date.month
            df['months_from_start'] = ((df['term_date'].dt.year - min_date.year) * 12 +  # type: ignore
                                       (df['term_date'].dt.month - min_date.month))  # type: ignore
        
        # Mevsim bilgisi ekle (1: İlkbahar, 2: Yaz, 3: Sonbahar, 4: Kış)
        if 'month' in df.columns:
            df['season'] = df['month'].apply(self._get_season)

        # Kış/yaz ayları binary feature
        if 'month' in df.columns:
            df['is_summer'] = df['month'].isin([6, 7, 8]).astype(int)  # Yaz ayları
            df['is_winter'] = df['month'].isin([12, 1, 2]).astype(int)  # Kış ayları

        return df

    def _calculate_avg_unit_price(self, df: pd.DataFrame) -> float:
        """
        Ortalama birim fiyat hesapla (TL/kWh)

        visualizer.py ile aynı mantığı kullan:
        - Tüketim: Direkt sum()
        - Maliyet: Unique term bazında sum() (tekrarları önle)

        Args:
            df: Ham veri (merged DataFrame)

        Returns:
            Ortalama birim fiyat (TL/kWh)
        """
        try:
            # ÖNEMLİ: Her iki hesaplama da UNIQUE term bazında yapılmalı
            df_unique = df.drop_duplicates(subset=['accrual_term_id'])

            # Tüketim: Unique term bazında
            total_consumption = df_unique['total_consumption'].sum()

            # Maliyet: Unique term bazında
            cost_column = 'term_total_cost' if 'term_total_cost' in df_unique.columns else 'amount'
            total_cost = df_unique[cost_column].sum()

            # Birim fiyat hesapla
            if total_consumption > 0:
                unit_price = total_cost / total_consumption
                return unit_price
            else:
                return 6.59  # Default (ortalama birim fiyat)
        except Exception as e:
            print(f"  [HATA] Birim fiyat hesaplanamadi: {e}")
            return 6.59  # Default

    def _calculate_category_distribution(self, df: pd.DataFrame) -> Dict:
        """
        Tarife kategorilerine göre tüketim dağılımı ve birim fiyatları hesapla

        Args:
            df: Ham veri (merged DataFrame)

        Returns:
            Kategori bazlı dağılım dictionary:
            {
                '4OG': {'ratio': 0.515, 'unit_price': 4.46, 'consumption': 110000000, 'cost': 490000000},
                '4AG': {'ratio': 0.270, 'unit_price': 2.14, 'consumption': 58000000, 'cost': 124000000},
                ...
            }
        """
        try:
            if 'fee_code' not in df.columns:
                print("  [UYARI] fee_code kolonu bulunamadi, kategori bazli hesaplama yapilamiyor")
                return {}

            # Tarife kategorisini fee_code'dan çıkar (örn: "4OG_GUN" -> "4OG")
            df_analysis = df.copy()
            df_analysis['tariff_category'] = df_analysis['fee_code'].str.split('_').str[0]

            # ÖNEMLİ: Aykırı değerleri filtrele (data_processor.py ile aynı mantık)
            # Sadece tüketimi olan ve makul birim fiyatlı fee'leri kullan
            df_analysis = df_analysis[
                (df_analysis['consumption'].notna()) &
                (df_analysis['consumption'] > 0) &
                (df_analysis['unit_price'].notna()) &
                (df_analysis['unit_price'] > 0) &
                (df_analysis['unit_price'] <= 10.0)  # Makul üst sınır
            ]

            print(f"  [DEBUG] Kategori dagilimi icin filtrelenmis fee sayisi: {len(df_analysis)}")

            # Her kategori için toplam tüketim ve maliyet hesapla
            # ÖNEMLİ: amount kullan (fee seviyesinde), term_total_cost değil!
            category_stats = {}

            # Kategorilere göre group by
            for category in df_analysis['tariff_category'].unique():
                if pd.isna(category):
                    continue

                # Bu kategoriye ait tüm kayıtlar
                cat_data = df_analysis[df_analysis['tariff_category'] == category]

                # Tüketim: consumption kolonu (fee seviyesinde, unique olması gerek)
                # Her fee için bir consumption var, topla
                cat_consumption = cat_data['consumption'].sum()

                # Maliyet: amount (fee seviyesinde maliyet, NOT term_total_cost!)
                cat_cost = cat_data['amount'].sum()

                # Birim fiyat hesapla
                if cat_consumption > 0:
                    cat_unit_price = cat_cost / cat_consumption
                else:
                    cat_unit_price = 0

                category_stats[category] = {
                    'consumption': cat_consumption,
                    'cost': cat_cost,
                    'unit_price': cat_unit_price
                }

            # Toplam tüketim
            total_consumption = sum(cat['consumption'] for cat in category_stats.values())

            # Her kategori için tüketim oranını hesapla
            for category in category_stats:
                if total_consumption > 0:
                    category_stats[category]['ratio'] = category_stats[category]['consumption'] / total_consumption
                else:
                    category_stats[category]['ratio'] = 0

            return category_stats

        except Exception as e:
            print(f"  [HATA] Kategori dagilimi hesaplanamadi: {e}")
            return {}

    def _calculate_category_based_cost(self, consumption: float) -> float:
        """
        Kategori bazlı maliyet hesapla

        Args:
            consumption: Toplam tüketim (kWh)

        Returns:
            Kategori dağılımına göre hesaplanan toplam maliyet (TL)
        """
        if not self.category_distribution:
            # Eğer kategori dağılımı yoksa, ortalama birim fiyat kullan
            return consumption * self.avg_unit_price

        total_cost = 0
        for _, data in self.category_distribution.items():
            # Bu kategorinin tüketim payı
            category_consumption = consumption * data['ratio']
            # Bu kategorinin maliyeti
            category_cost = category_consumption * data['unit_price']
            total_cost += category_cost

        return total_cost

    def _get_season(self, month: int) -> int:
        """
        Aydan mevsim bilgisi çıkar

        Args:
            month: Ay numarası (1-12)

        Returns:
            Mevsim kodu (1-4)
        """
        if month in [3, 4, 5]:
            return 1  # İlkbahar
        elif month in [6, 7, 8]:
            return 2  # Yaz
        elif month in [9, 10, 11]:
            return 3  # Sonbahar
        else:
            return 4  # Kış

    def _compare_models(self, X_train, X_test, y_train, y_test) -> Dict:
        """
        Farklı ML modellerini karşılaştır ve en iyisini seç

        Args:
            X_train, X_test: Eğitim ve test features
            y_train, y_test: Eğitim ve test hedef değişkenleri

        Returns:
            Model karşılaştırma sonuçları
        """
        print("  [ML] Model karşılaştırması yapılıyor...")

        models_to_test = {
            'Linear Regression': LinearRegression(),
            'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
        }

        # XGBoost varsa ekle
        if XGBOOST_AVAILABLE:
            models_to_test['XGBoost'] = XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1
            )

        # LightGBM varsa ekle
        if LIGHTGBM_AVAILABLE:
            models_to_test['LightGBM'] = LGBMRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1,
                verbose=-1
            )

        results = {}
        best_r2 = -999
        best_model = None
        best_model_name = None

        for name, model in models_to_test.items():
            # Eğit
            model.fit(X_train, y_train)

            # Tahmin yap
            y_pred = model.predict(X_test)

            # Metrikleri hesapla
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            # MAPE hesapla (yüzde hata)
            try:
                mape = mean_absolute_percentage_error(y_test, y_pred) * 100
            except:
                mape = 0

            results[name] = {
                'MAE': mae,
                'R2': r2,
                'MAPE': mape,
                'model': model
            }

            print(f"    - {name}: R²={r2:.3f}, MAE={mae:,.0f}, MAPE={mape:.1f}%")

            # En iyi modeli seç (R² skoruna göre)
            if r2 > best_r2:
                best_r2 = r2
                best_model = model
                best_model_name = name

        print(f"  [OK] En iyi model: {best_model_name} (R²={best_r2:.3f})")

        return {
            'results': results,
            'best_model': best_model,
            'best_model_name': best_model_name
        }

    def train_models(self, df: pd.DataFrame) -> Dict:
        """
        Tüketim ve maliyet tahmin modellerini eğit

        Args:
            df: Eğitim verisi

        Returns:
            Model performans metrikleri
        """
        print("[ML] Machine Learning modelleri egitiliyor...")

        # ÖNEMLİ: Ortalama birim fiyat hesaplama için RAW veriyi sakla
        raw_df = df.copy()

        # Duplikatları temizle - Her term bir kez
        if 'accrual_term_id' in df.columns:
            df = df.drop_duplicates(subset=['accrual_term_id'])
            print(f"  [INFO] Unique term sayisi: {len(df)}")

        # Özellikleri hazırla
        df = self.prepare_features(df)

        # ÖNEMLİ: Yıl-ay bazında aggregate et!
        # Her ay için toplam tüketim ve maliyet hesapla
        print(f"  [INFO] Yil-ay bazinda aggregate ediliyor...")

        # Doğru maliyet kolonunu belirle (term_total_cost veya amount)
        cost_column = 'term_total_cost' if 'term_total_cost' in df.columns else 'amount'

        monthly_agg = df.groupby(['year', 'month']).agg({
            'total_consumption': 'sum',
            cost_column: 'sum'
        }).reset_index()

        # Kolon ismini standartlaştır (ileride kullanım için)
        if cost_column == 'term_total_cost':
            monthly_agg = monthly_agg.rename(columns={'term_total_cost': 'grand_total'})

        # OUTLIER TEMİZLİĞİ: IQR metodu ile SADECE AŞIRI UÇ DEĞERLERİ temizle
        # 5.0 katsayı = Çok yumuşak filtreleme, sadece gerçekten aşırı olanları atar
        Q1_cons = monthly_agg['total_consumption'].quantile(0.25)
        Q3_cons = monthly_agg['total_consumption'].quantile(0.75)
        IQR_cons = Q3_cons - Q1_cons
        lower_bound = Q1_cons - 5.0 * IQR_cons  # Çok yumuşak alt sınır
        upper_bound = Q3_cons + 5.0 * IQR_cons  # Çok yumuşak üst sınır

        # Sadece AŞIRI uç değerleri temizle
        before_count = len(monthly_agg)
        monthly_agg = monthly_agg[
            (monthly_agg['total_consumption'] >= lower_bound) &
            (monthly_agg['total_consumption'] <= upper_bound)
        ]
        print(f"  [INFO] Outlier temizlendi (5.0x): {before_count} -> {len(monthly_agg)} kayit")

        # Özellikleri tekrar hazırla (aggregated veri için)
        # months_from_start için referans tarih
        if self.min_date is None:
            # İlk tarihi yaklaşık olarak hesapla
            self.reference_year = monthly_agg['year'].min()
            self.reference_month = monthly_agg['month'].min()

        # Feature'ları ekle
        # None kontrolü ile güvenli hesaplama
        ref_year = self.reference_year if self.reference_year is not None else monthly_agg['year'].min()
        ref_month = self.reference_month if self.reference_month is not None else 1
        monthly_agg['months_from_start'] = ((monthly_agg['year'] - ref_year) * 12 +
                                            (monthly_agg['month'] - ref_month))
        monthly_agg['season'] = monthly_agg['month'].apply(self._get_season)
        monthly_agg['quarter'] = ((monthly_agg['month'] - 1) // 3 + 1)
        monthly_agg['is_summer'] = monthly_agg['month'].isin([6, 7, 8]).astype(int)
        monthly_agg['is_winter'] = monthly_agg['month'].isin([12, 1, 2]).astype(int)

        print(f"  [INFO] Aggregate sonrasi {len(monthly_agg)} aylik veri")

        # Tüketim tahmini için veri hazırlığı
        consumption_data = monthly_agg[monthly_agg['total_consumption'].notna()].copy()
        
        # Özellik sütunları - Daha fazla feature eklendi
        self.feature_columns = ['year', 'month', 'months_from_start', 'season', 'quarter',
                                'is_summer', 'is_winter']
        
        # Eksik değerleri kontrol et ve temizle
        consumption_data = consumption_data.dropna(subset=self.feature_columns + ['total_consumption'])

        if len(consumption_data) < 10:
            print("[HATA] Yeterli veri yok! En az 10 kayit gerekli.")
            # None yerine error bilgisi içeren dict döndür
            return {
                'consumption_mae': 0,
                'consumption_r2': 0,
                'avg_unit_price': self.avg_unit_price,
                'training_samples': len(consumption_data),
                'error': 'Yetersiz veri - en az 10 kayıt gerekli'
            }
        
        # Tüketim modeli için X ve y
        X_consumption = consumption_data[self.feature_columns]
        y_consumption = consumption_data['total_consumption']

        # Veri kalitesi kontrolü (opsiyonel - production'da kapatılabilir)

        # Veriyi eğitim ve test setlerine ayır (Az veri olduğu için %90 eğitim, %10 test)
        X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
            X_consumption, y_consumption, test_size=0.1, random_state=42
        )

        # Feature'ları normalize et (Scaler'ı eğit)
        X_train_c_scaled = self.scaler.fit_transform(X_train_c)
        X_test_c_scaled = self.scaler.transform(X_test_c)

        # 🚀 RANDOM FOREST MODELİ - Direkt kullan, karşılaştırma yok!
        print("  [ML] Random Forest modeli egitiliyor...")
        self.consumption_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.best_model_name = "Random Forest"

        # Modeli eğit
        self.consumption_model.fit(X_train_c_scaled, y_train_c)
        y_pred_c = self.consumption_model.predict(X_test_c_scaled)

        # Performans metrikleri
        mae_consumption = mean_absolute_error(y_test_c, y_pred_c)
        r2_consumption = r2_score(y_test_c, y_pred_c)

        print(f"  [OK] Random Forest modeli egitildi:")
        print(f"    - MAE: {mae_consumption:,.2f} kWh")
        print(f"    - R2 Score: {r2_consumption:.3f}")

        # Ortalama birim fiyatı hesapla (DOĞRU YÖNTEM - visualizer.py ile aynı)
        # ÖNEMLİ: raw_df kullan (aggregated değil!)
        self.avg_unit_price = self._calculate_avg_unit_price(raw_df)
        print(f"  [OK] Ortalama birim fiyat hesaplandi:")
        print(f"    - {self.avg_unit_price:.2f} TL/kWh")

        # Kategori bazlı dağılımı hesapla (tahminlerde kullanılacak)
        self.category_distribution = self._calculate_category_distribution(raw_df)
        if self.category_distribution:
            print(f"  [OK] Kategori bazli dagilim hesaplandi:")
            for category, data in sorted(self.category_distribution.items(),
                                        key=lambda x: x[1]['ratio'], reverse=True):
                print(f"    - {category}: %{data['ratio']*100:.1f} tuketim, "
                      f"{data['unit_price']:.2f} TL/kWh birim fiyat")
            print(f"  [OK] Maliyet tahmini: Kategori bazli hesaplama kullanilacak")
        else:
            print(f"  [UYARI] Kategori bazli hesaplama yapilamiyor, ortalama birim fiyat kullanilacak")
            print(f"    - Maliyet tahmini: Tuketim x {self.avg_unit_price:.2f} TL/kWh")

        self.is_trained = True
        print("[OK] Model egitimi tamamlandi!\n")

        return {
            'consumption_mae': mae_consumption,
            'consumption_r2': r2_consumption,
            'avg_unit_price': self.avg_unit_price,
            'training_samples': len(consumption_data),
            'best_model': self.best_model_name
        }
    
    def predict_future(self, months_ahead: int = 6) -> pd.DataFrame | None:
        """
        Gelecek aylar için tahmin yap
        
        Args:
            months_ahead: Kaç ay ilerisi için tahmin yapılacak
            
        Returns:
            Tahminleri içeren DataFrame
        """
        if not self.is_trained or self.consumption_model is None:
            print("[HATA] Model henuz egitilmedi! Once train_models() cagirin.")
            return None

        print(f"[TAHMIN] Gelecek {months_ahead} ay icin tahminler yapiliyor...")

        # Gelecek tarihler oluştur (ay bazında, gün sayısı değil!)
        today = datetime.now()
        future_dates = [today + relativedelta(months=i) for i in range(1, months_ahead + 1)]
        
        predictions = []
        
        for date in future_dates:
            # Özellikleri hazırla
            # months_from_start: Başlangıçtan bu tarihe kadar geçen ay sayısı
            # None kontrolü ile güvenli hesaplama
            ref_year = self.reference_year if self.reference_year is not None else datetime.now().year
            ref_month = self.reference_month if self.reference_month is not None else 1
            months_from_start = ((date.year - ref_year) * 12 +
                                (date.month - ref_month))

            features = {
                'year': date.year,
                'month': date.month,
                'months_from_start': months_from_start,
                'season': self._get_season(date.month),
                'quarter': (date.month - 1) // 3 + 1,
                'is_summer': 1 if date.month in [6, 7, 8] else 0,
                'is_winter': 1 if date.month in [12, 1, 2] else 0
            }
            
            # DataFrame'e çevir
            X_future = pd.DataFrame([features])[self.feature_columns]

            # Feature'ları normalize et
            X_future_scaled = self.scaler.transform(X_future)

            # Tahmin yap (normalized data ile)
            consumption_pred = self.consumption_model.predict(X_future_scaled)[0]

            # Maliyet = Kategori bazlı hesaplama (tarife kategorilerine göre)
            cost_pred = self._calculate_category_based_cost(consumption_pred)

            predictions.append({
                'Tarih': date.strftime('%Y-%m'),
                'Tahmini_Tuketim_kWh': consumption_pred,
                'Tahmini_Maliyet_TL': cost_pred
            })
        
        df_predictions = pd.DataFrame(predictions)
        print("[OK] Tahminler hazir!\n")

        return df_predictions
    
    def predict_next_month(self) -> Dict | None:
        """
        Önümüzdeki ay için detaylı tahmin yap
        
        Returns:
            Tahmin bilgilerini içeren dictionary
        """
        if not self.is_trained or self.consumption_model is None:
            return None

        # Gelecek ay (ay bazında, gün sayısı değil!)
        next_month = datetime.now() + relativedelta(months=1)

        # months_from_start hesapla
        # None kontrolü ile güvenli hesaplama
        ref_year = self.reference_year if self.reference_year is not None else datetime.now().year
        ref_month = self.reference_month if self.reference_month is not None else 1
        months_from_start = ((next_month.year - ref_year) * 12 +
                            (next_month.month - ref_month))

        features = {
            'year': next_month.year,
            'month': next_month.month,
            'months_from_start': months_from_start,
            'season': self._get_season(next_month.month),
            'quarter': (next_month.month - 1) // 3 + 1,
            'is_summer': 1 if next_month.month in [6, 7, 8] else 0,
            'is_winter': 1 if next_month.month in [12, 1, 2] else 0
        }
        
        X_future = pd.DataFrame([features])[self.feature_columns]

        # Normalize et
        X_future_scaled = self.scaler.transform(X_future)

        consumption_pred = self.consumption_model.predict(X_future_scaled)[0]
        # Maliyet = Kategori bazlı hesaplama (tarife kategorilerine göre)
        cost_pred = self._calculate_category_based_cost(consumption_pred)

        return {
            'month': next_month.strftime('%B %Y'),
            'consumption': consumption_pred,
            'cost': cost_pred,
            'season': ['İlkbahar', 'Yaz', 'Sonbahar', 'Kış'][features['season'] - 1]
        }
    
    def get_yearly_forecast(self, year: int) -> pd.DataFrame | None:
        """
        Belirli bir yıl için aylık tahminler oluştur
        
        Args:
            year: Tahmin yapılacak yıl
            
        Returns:
            Yıllık tahminler DataFrame'i
        """
        if not self.is_trained or self.consumption_model is None:
            return None

        predictions = []

        for month in range(1, 13):
            # months_from_start hesapla
            # None kontrolü ile güvenli hesaplama
            ref_year = self.reference_year if self.reference_year is not None else datetime.now().year
            ref_month = self.reference_month if self.reference_month is not None else 1
            months_from_start = ((year - ref_year) * 12 +
                                (month - ref_month))

            features = {
                'year': year,
                'month': month,
                'months_from_start': months_from_start,
                'season': self._get_season(month),
                'quarter': (month - 1) // 3 + 1,
                'is_summer': 1 if month in [6, 7, 8] else 0,
                'is_winter': 1 if month in [12, 1, 2] else 0
            }
            
            X_future = pd.DataFrame([features])[self.feature_columns]

            # Normalize et
            X_future_scaled = self.scaler.transform(X_future)

            consumption_pred = self.consumption_model.predict(X_future_scaled)[0]
            # Maliyet = Kategori bazlı hesaplama (tarife kategorilerine göre)
            cost_pred = self._calculate_category_based_cost(consumption_pred)

            month_names = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
                          'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']

            predictions.append({
                'Ay': month_names[month - 1],
                'Tuketim_kWh': consumption_pred,
                'Maliyet_TL': cost_pred
            })
        
        return pd.DataFrame(predictions)
    
    def compare_prediction_vs_actual(self, df: pd.DataFrame) -> pd.DataFrame | None:
        """
        Gerçek değerler ile tahminleri karşılaştır
        
        Args:
            df: Gerçek verileri içeren DataFrame
            
        Returns:
            Karşılaştırma sonuçları
        """
        if not self.is_trained or self.consumption_model is None:
            return None

        df = self.prepare_features(df)
        df = df.dropna(subset=self.feature_columns + ['total_consumption'])
        
        X = df[self.feature_columns]

        # Tahminleri yap
        consumption_predictions = self.consumption_model.predict(X)
        # Maliyet = Kategori bazlı hesaplama (tarife kategorilerine göre)
        cost_predictions = np.array([self._calculate_category_based_cost(cons) for cons in consumption_predictions])

        # Doğru maliyet kolonunu belirle
        cost_column = 'term_total_cost' if 'term_total_cost' in df.columns else 'amount'

        # Karşılaştırma DataFrame'i oluştur
        comparison = pd.DataFrame({
            'Tarih': df['term_date'],
            'Gercek_Tuketim': df['total_consumption'],
            'Tahmin_Tuketim': consumption_predictions,
            'Tuketim_Fark': df['total_consumption'] - consumption_predictions,
            'Gercek_Maliyet': df[cost_column],
            'Tahmin_Maliyet': cost_predictions,
            'Maliyet_Fark': df[cost_column] - cost_predictions
        })
        
        return comparison