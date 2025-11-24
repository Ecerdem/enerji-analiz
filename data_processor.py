"""
Enerji Tüketim Veri İşleme Modülü
Bu modül veritabanından verileri okur, temizler ve analiz için hazırlar.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Tuple, Optional
import os
from config import Config
from database import get_database_manager

class EnergyDataProcessor:
    """
    Enerji fatura verilerini işleyen ana sınıf.
    Veritabanından veri okur, birleştirir ve analiz için hazırlar.
    """

    def __init__(self):
        """
        Veri işleyiciyi başlat
        """
        self.db_manager = get_database_manager()

        self.df_accruals = None
        self.df_fees = None
        self.df_terms = None
        self.df_consumptions = None
        self.df_merged = None
        
    def load_data(self) -> bool:
        """
        Veritabanından verileri yükle

        Returns:
            bool: Yükleme başarılıysa True, değilse False
        """
        return self._load_from_database()

    def _load_from_database(self) -> bool:
        """
        Veritabanından tüm tabloları yükle

        Returns:
            bool: Yükleme başarılıysa True, değilse False
        """
        try:
            print("[YUKLE] Veritabanindan veriler yukleniyor...")

            engine = self.db_manager.get_engine()

            # bi_accruals - Ana fatura bilgileri
            query_accruals = f"SELECT * FROM {Config.get_full_table_name(Config.DB_TABLE_ACCRUALS)}"
            self.df_accruals = pd.read_sql(query_accruals, engine)
            print(f"[OK] {Config.DB_TABLE_ACCRUALS} yuklendi: {len(self.df_accruals)} kayit")

            # bi_accrual_fees - Fatura ücret detayları
            query_fees = f"SELECT * FROM {Config.get_full_table_name(Config.DB_TABLE_ACCRUAL_FEES)}"
            self.df_fees = pd.read_sql(query_fees, engine)
            print(f"[OK] {Config.DB_TABLE_ACCRUAL_FEES} yuklendi: {len(self.df_fees)} kayit")

            # bi_accrual_terms - Fatura dönem bilgileri
            query_terms = f"SELECT * FROM {Config.get_full_table_name(Config.DB_TABLE_ACCRUAL_TERMS)}"
            self.df_terms = pd.read_sql(query_terms, engine)
            print(f"[OK] {Config.DB_TABLE_ACCRUAL_TERMS} yuklendi: {len(self.df_terms)} kayit")

            # bi_accrual_fee_consumptions - Tüketim detayları
            query_consumptions = f"SELECT * FROM {Config.get_full_table_name(Config.DB_TABLE_ACCRUAL_FEE_CONSUMPTIONS)}"
            self.df_consumptions = pd.read_sql(query_consumptions, engine)
            print(f"[OK] {Config.DB_TABLE_ACCRUAL_FEE_CONSUMPTIONS} yuklendi: {len(self.df_consumptions)} kayit")

            print("[OK] Veritabanindan tum tablolar basariyla yuklendi!\n")
            return True

        except Exception as e:
            print(f"[HATA] Veritabani yuklemede hata: {e}")
            return False

    def clean_and_prepare(self):
        """
        Verileri temizle ve analiz için hazırla
        - Tarih formatlarını düzelt
        - Eksik verileri kontrol et
        - Veri tiplerini düzelt
        """
        print("[TEMIZLE] Veriler temizleniyor ve hazirlaniyor...")

        # Tarih sütunlarını datetime formatına çevir
        # Format: YYYYMMDDHHmmss (örn: 20250226141640)
        if 'term_date' in self.df_terms.columns:
            self.df_terms['term_date'] = pd.to_datetime(
                self.df_terms['term_date'],
                format='%Y%m%d%H%M%S',
                errors='coerce'
            )
            # Yıl ve ay bilgilerini ayrı sütunlar olarak ekle
            self.df_terms['year'] = self.df_terms['term_date'].dt.year
            self.df_terms['month'] = self.df_terms['term_date'].dt.month
            print("  [OK] Tarih formatlari duzeltildi")

        # Accruals tablosundaki tarih sütunları
        date_columns = ['accrual_date', 'accrual_start_date', 'accrual_end_date']
        for col in date_columns:
            if col in self.df_accruals.columns:
                self.df_accruals[col] = pd.to_datetime(
                    self.df_accruals[col],
                    format='%Y%m%d%H%M%S',
                    errors='coerce'
                )

        # Terms tablosundaki diğer tarih sütunları
        term_date_columns = ['start_date', 'end_date']
        for col in term_date_columns:
            if col in self.df_terms.columns:
                self.df_terms[col] = pd.to_datetime(
                    self.df_terms[col],
                    format='%Y%m%d%H%M%S',
                    errors='coerce'
                )
        
        # Sayısal sütunları kontrol et ve düzelt
        if 'amount' in self.df_fees.columns:
            self.df_fees['amount'] = pd.to_numeric(self.df_fees['amount'], errors='coerce')
        
        if 'unit_price' in self.df_fees.columns:
            self.df_fees['unit_price'] = pd.to_numeric(self.df_fees['unit_price'], errors='coerce')
        
        if 'consumption' in self.df_fees.columns:
            self.df_fees['consumption'] = pd.to_numeric(self.df_fees['consumption'], errors='coerce')
        
        if 'billable_channel_consumption' in self.df_consumptions.columns:
            self.df_consumptions['billable_channel_consumption'] = pd.to_numeric(
                self.df_consumptions['billable_channel_consumption'], errors='coerce'
            )
        
        print("  [OK] Sayisal degerler duzeltildi")
        
        # Eksik verileri kontrol et
        print("\n[VERI] Eksik Veri Kontrolu:")
        print(f"  - Accruals eksik: {self.df_accruals.isnull().sum().sum()}")
        print(f"  - Terms eksik: {self.df_terms.isnull().sum().sum()}")
        print(f"  - Consumptions eksik: {self.df_consumptions.isnull().sum().sum()}")

        print("[OK] Veri temizleme tamamlandi!\n")
    
    def merge_data(self):
        """
        Tüm tabloları birleştir ve analiz için tek bir DataFrame oluştur
        """
        print("[BIRLESTIR] Tablolar birlestiriliyor...")

        # 1. Accruals ve Terms'i birleştir
        # bi_accruals.id = bi_accrual_terms.accrual_id
        df_merged = pd.merge(
            self.df_accruals,
            self.df_terms,
            left_on='id',
            right_on='accrual_id',
            how='inner',  # inner join ile sadece eşleşenleri al
            suffixes=('', '_term')
        )
        print(f"  [OK] Accruals + Terms birlestirildi: {len(df_merged)} kayit")

        # 2. Fees tablosunu ekle
        # bi_accrual_terms.id = bi_accrual_fees.accrual_term_id
        # İlk merge'den sonra terms'deki 'id' sütunu 'id_term' olarak geldi
        df_merged = pd.merge(
            df_merged,
            self.df_fees,
            left_on='id_term',  # terms tablosundaki id (suffix almış hali)
            right_on='accrual_term_id',
            how='inner',
            suffixes=('', '_fee')
        )
        print(f"  [OK] Fees eklendi: {len(df_merged)} kayit")

        # 3. Consumptions tablosunu ekle
        # bi_accrual_fees.id = bi_accrual_fee_consumptions.accrual_fee_id
        # Fees'deki 'id' sütunu şimdi 'id_fee' olarak var
        df_merged = pd.merge(
            df_merged,
            self.df_consumptions,
            left_on='id_fee',
            right_on='accrual_fee_id',
            how='left',  # left join çünkü tüm fee'lerde consumption olmayabilir
            suffixes=('', '_consumption')
        )
        print(f"  [OK] Consumptions eklendi: {len(df_merged)} kayit")

        # 4. Hesaplanan sütunlar ekle

        # Fee code'dan prefix çıkar (4AG, 4OG, URT, KAG, KOG, vb.)
        if 'fee_code' in df_merged.columns:
            # Prefix'i al (ilk 3-4 karakter veya ilk underscore'a kadar)
            df_merged['fee_prefix'] = df_merged['fee_code'].str.split('_').str[0]
            print(f"  [OK] Fee prefix'leri cikarildi")

        # amount zaten unit_price × consumption olarak hesaplanmış durumda
        # KDV eklemiyoruz, direkt amount kullanıyoruz

        # Toplam tüketim hesapla (accrual_term_id bazında)
        if 'consumption' in df_merged.columns:
            # Her term için toplam tüketim (fee consumption'larının toplamı)
            consumption_totals = df_merged.groupby('accrual_term_id')['consumption'].sum().reset_index()
            consumption_totals.columns = ['accrual_term_id', 'total_consumption']

            # Merge et
            df_merged = df_merged.drop(columns=['total_consumption'], errors='ignore')
            df_merged = pd.merge(
                df_merged,
                consumption_totals,
                on='accrual_term_id',
                how='left'
            )
            print(f"  [OK] Toplam tuketim hesaplandi")

        # Her term için toplam maliyet hesapla (KDV'siz, direkt amount toplamı)
        # SADECE consumption > 0 olan fee'leri kullan (sabit ücretleri hariç tut)
        if 'amount' in df_merged.columns and 'accrual_term_id' in df_merged.columns:
            # Eski term_total_cost sütununu sil (varsa)
            df_merged = df_merged.drop(columns=['term_total_cost'], errors='ignore')

            # Sadece tüketim olan fee'lerin maliyetini hesapla
            total_fees = len(df_merged)
            df_with_consumption = df_merged[
                (df_merged['consumption'].notna()) &
                (df_merged['consumption'] > 0) &
                (df_merged['unit_price'].notna()) &
                (df_merged['unit_price'] > 0) &
                (df_merged['unit_price'] <= 5.0)  # Anormal unit_price'ları filtrele
            ]
            fees_with_consumption = len(df_with_consumption)

            print(f"  [DEBUG] Toplam fee sayisi: {total_fees}")
            print(f"  [DEBUG] Tuketimi olan fee sayisi: {fees_with_consumption}")

            cost_totals = df_with_consumption.groupby('accrual_term_id')['amount'].sum().reset_index()
            cost_totals.columns = ['accrual_term_id', 'term_total_cost']

            # Merge et
            df_merged = pd.merge(
                df_merged,
                cost_totals,
                on='accrual_term_id',
                how='left'
            )
            print(f"  [OK] Toplam maliyet hesaplandi (Sadece tuketim olan fee'ler, KDV'siz)")

        # Sütun isimlerini standardize et
        if 'billable_channel_consumption' in df_merged.columns:
            df_merged['consumption_value'] = df_merged['billable_channel_consumption'].fillna(0)

        if 'channel_key' in df_merged.columns:
            df_merged['time_frame'] = df_merged['channel_key'].fillna('UNKNOWN')

        # Null değerleri temizle
        df_merged['total_consumption'] = df_merged['total_consumption'].fillna(0)
        df_merged['amount'] = df_merged['amount'].fillna(0)
        df_merged['term_total_cost'] = df_merged['term_total_cost'].fillna(0)

        self.df_merged = df_merged
        print("[OK] Tum tablolar basariyla birlestirildi!\n")

        # Özet için unique term bazında hesapla (her term bir kez sayılsın)
        df_unique_summary = df_merged.drop_duplicates(subset=['accrual_term_id'])

        print(f"[OZET] Toplam kayit sayisi: {len(df_merged)}")
        print(f"[OZET] Unique term sayisi: {len(df_unique_summary)}")
        print(f"[OZET] Tarih araligi: {df_merged['term_date'].min()} - {df_merged['term_date'].max()}")
        print(f"[OZET] Toplam tuketim: {df_unique_summary['total_consumption'].sum():,.2f} kWh")
        print(f"[OZET] Toplam maliyet (KDV'siz): TL {df_unique_summary['term_total_cost'].sum():,.2f}")

        # Yıllara göre dağılım
        print("\n[YILLIK DAGILIM]")
        yearly_summary = df_unique_summary.groupby('year').agg({
            'total_consumption': 'sum',
            'term_total_cost': 'sum'
        }).reset_index()
        for _, row in yearly_summary.iterrows():
            birim_fiyat = row['term_total_cost'] / row['total_consumption'] if row['total_consumption'] > 0 else 0
            print(f"  {int(row['year'])}: {row['total_consumption']:,.0f} kWh -> {row['term_total_cost']:,.2f} TL (Birim: {birim_fiyat:.2f} TL/kWh)")

        # Unit_price değerlerinin yıllara göre dağılımı
        print("\n[UNIT_PRICE ANALIZI - Sadece consumption > 0 olanlar]")
        df_with_consumption = df_merged[(df_merged['consumption'].notna()) & (df_merged['consumption'] > 0)]
        unit_price_by_year = df_with_consumption.groupby('year')['unit_price'].agg(['mean', 'min', 'max', 'count']).reset_index()
        for _, row in unit_price_by_year.iterrows():
            print(f"  {int(row['year'])}: Ort={row['mean']:.2f} TL/kWh, Min={row['min']:.2f}, Max={row['max']:.2f}, Fee sayisi={int(row['count'])}")
        print()
        
    def get_processed_data(self) -> pd.DataFrame:
        """
        İşlenmiş veriyi döndür
        
        Returns:
            Birleştirilmiş ve işlenmiş DataFrame
        """
        return self.df_merged
    
    def get_summary_statistics(self) -> Dict:
        """
        Veri hakkında özet istatistikler

        Returns:
            İstatistikleri içeren dictionary
        """
        if self.df_merged is None:
            return None

        # Unique term bazında hesaplama (her term için bir kez say)
        df_unique = self.df_merged.drop_duplicates(subset=['accrual_term_id'])

        stats = {
            'total_records': len(self.df_merged),
            'total_consumption': df_unique['total_consumption'].sum() if 'total_consumption' in df_unique.columns else 0,
            'total_cost': df_unique['term_total_cost'].sum() if 'term_total_cost' in df_unique.columns else 0,
            'date_range': {
                'start': self.df_merged['term_date'].min() if 'term_date' in self.df_merged.columns else None,
                'end': self.df_merged['term_date'].max() if 'term_date' in self.df_merged.columns else None
            },
            'unique_accruals': self.df_merged['accrual_id'].nunique() if 'accrual_id' in self.df_merged.columns else 0,
            'unique_prefixes': self.df_merged['fee_prefix'].nunique() if 'fee_prefix' in self.df_merged.columns else 0
        }

        return stats
    
    def export_to_csv(self, filename: str = "processed_data.csv"):
        """
        İşlenmiş veriyi CSV olarak dışa aktar
        
        Args:
            filename: Kaydedilecek dosya adı
        """
        if self.df_merged is not None:
            self.df_merged.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"[OK] Veri '{filename}' dosyasina kaydedildi!")
        else:
            print("[HATA] Henuz islenmis veri yok!")