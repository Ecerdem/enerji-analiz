"""
Enerji Tüketim Analiz ve Tahmin Sistemi
Streamlit Web Uygulaması - Ana Dosya
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_processor import EnergyDataProcessor
from predictor import EnergyPredictor
from visualizer import EnergyVisualizer
from config import Config
import warnings
warnings.filterwarnings('ignore')


# Sayfa yapılandırması
st.set_page_config(
    page_title="Enerji Analiz Sistemi",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS ile özel stil
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stAlert {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_and_process_data():
    """
    Verileri veritabanından veya CSV'den yükle ve işle (cache'lenir, tekrar yüklemeyi önler)
    """
    # Config.USE_DATABASE değerine göre otomatik olarak veri kaynağı seçilir
    processor = EnergyDataProcessor(data_folder="data")

    if processor.load_data():
        processor.clean_and_prepare()
        processor.merge_data()
        return processor.get_processed_data()
    return None


@st.cache_resource
def train_prediction_model(df):
    """
ML modelini eğit (cache'lenir, tekrar eğitmeyi önler)
    """
    predictor = EnergyPredictor()
    metrics = predictor.train_models(df)
    return predictor, metrics


def main():
    """Ana uygulama fonksiyonu"""
    
    # Başlık
    st.markdown('<h1 class="main-header">⚡ Enerji Tüketim Analiz Sistemi</h1>', 
                unsafe_allow_html=True)
    
    # Sidebar - Menü
    st.sidebar.title("📊 Menü")
    menu = st.sidebar.radio(
        "Menü",
        ["Ana Sayfa", "Tüketim Analizi", "Maliyet Analizi",
         "Tahminler", "Detaylı Raporlar"],
        label_visibility="collapsed"  # "Menü" yazısını gizle
    )
    
    # Veri yükleme durumu
    with st.spinner('📂 Veriler yükleniyor...'):
        df = load_and_process_data()
    
    if df is None:
        st.error("❌ Veri yüklenemedi!")

        if Config.USE_DATABASE:
            st.warning("""
            🗄️ **Veritabanı Bağlantısı Kullanılıyor**

            Lütfen kontrol edin:
            1. `.env` dosyasındaki veritabanı bağlantı bilgileri doğru mu?
            2. PostgreSQL sunucusu çalışıyor mu?
            3. Gerekli tablolar mevcut mu?
               - bi_accruals
               - bi_accrual_fees
               - bi_accrual_terms
               - bi_accrual_fee_consumptions
            """)
        else:
            st.info("""
            📁 **CSV Dosyaları Kullanılıyor**

            Gerekli dosyalar 'data' klasöründe:
            - bi_accruals.csv
            - bi_accrual_fees.csv
            - bi_accrual_terms.csv
            - bi_accrual_fee_consumptions.csv
            """)
        return
    
    # Görselleştirici oluştur
    visualizer = EnergyVisualizer()
    
    # ========================
    # ANA SAYFA
    # ========================
    if menu == "Ana Sayfa":
        st.header("Hoş Geldiniz! 👋")
        
        st.info("""
        Bu sistem, şirketinizin enerji tüketim verilerini analiz eder ve gelecek tahminleri sunar.
        Sol menüden istediğiniz analiz türünü seçebilirsiniz.
        """)
        
        # Özet metrikler
        metrics = visualizer.create_summary_metrics(df)
        
        st.subheader("📊 Genel Özet")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Toplam Tüketim",
                value=f"{metrics['total_consumption']:,.0f} kWh"
            )
        
        with col2:
            st.metric(
                label="Toplam Maliyet",
                value=f"₺{metrics['total_cost']:,.2f}"
            )
        
        with col3:
            st.metric(
                label="Aylık Ort. Tüketim",
                value=f"{metrics['avg_monthly_consumption']:,.0f} kWh"
            )
        
        with col4:
            st.metric(
                label="Aylık Ort. Maliyet",
                value=f"₺{metrics['avg_monthly_cost']:,.2f}"
            )
        
        # En yüksek ve en düşük tüketim ayları
        st.subheader("🔝 Dikkat Çeken Aylar")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"""
            **En Düşük Tüketim:**  
            📅 {metrics['min_consumption_month']}  
            ⚡ {metrics['min_consumption_value']:,.0f} kWh
            """)
        
        with col2:
            st.error(f"""
            **En Yüksek Tüketim:**  
            📅 {metrics['max_consumption_month']}  
            ⚡ {metrics['max_consumption_value']:,.0f} kWh
            """)
        
        # Hızlı grafikler
        st.subheader("📈 Hızlı Bakış")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_trend = visualizer.plot_consumption_trend(df)
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            fig_yearly = visualizer.plot_yearly_comparison(df)
            st.plotly_chart(fig_yearly, use_container_width=True)
    
    # ========================
    # TÜKETİM ANALİZİ
    # ========================
    elif menu == "Tüketim Analizi":
        st.header("📈 Enerji Tüketim Analizi")
        
        # Tüketim trendi
        st.subheader("Tüketim Trendi (Aylık Veriler)")
        fig_trend = visualizer.plot_consumption_trend(df)
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Mevsimsel Analiz
        st.subheader("Mevsimsel Analiz")
        fig_seasonal = visualizer.plot_seasonal_analysis(df)
        st.plotly_chart(fig_seasonal, use_container_width=True)
    
    # ========================
    # MALİYET ANALİZİ
    # ========================
    elif menu == "Maliyet Analizi":
        st.header("💰 Maliyet Analizi")
        
        # Maliyet grafiği
        st.subheader("Aylık Maliyet Trendi")
        fig_cost = visualizer.plot_cost_analysis(df)
        st.plotly_chart(fig_cost, use_container_width=True)
        
        # Yıllık karşılaştırma
        st.subheader("Yıllık Karşılaştırma")
        fig_yearly = visualizer.plot_yearly_comparison(df)
        st.plotly_chart(fig_yearly, use_container_width=True)
        
        # Maliyet özeti tablosu
        st.subheader("📊 Yıllık Maliyet Özeti")

        # Unique term bazında hesaplama
        df_unique = df.drop_duplicates(subset=['accrual_term_id'])

        # term_total_cost varsa onu kullan
        cost_column = 'term_total_cost' if 'term_total_cost' in df_unique.columns else 'amount'

        yearly_cost = df_unique.groupby('year').agg({
            cost_column: 'sum',
            'total_consumption': 'sum'
        }).reset_index()

        # Birim fiyat hesapla (TL/kWh) - sıfıra bölmeyi ve NaN'i önle, 2 ondalık yuvarlama
        yearly_cost['unit_price'] = yearly_cost.apply(
            lambda row: (round(row[cost_column] / row['total_consumption'], 2)
                        if pd.notna(row['total_consumption']) and row['total_consumption'] > 0
                        else 0),
            axis=1
        )

        # Float hassasiyet hatalarını düzelt
        yearly_cost['total_consumption'] = yearly_cost['total_consumption'].round(2)
        yearly_cost[cost_column] = yearly_cost[cost_column].round(2)

        # Kolonları yeniden düzenle (mantıklı sıralama: Yıl, Tüketim, Maliyet, Birim Fiyat)
        yearly_cost = yearly_cost[['year', 'total_consumption', cost_column, 'unit_price']]
        yearly_cost.columns = ['Yıl', 'Tüketim (kWh)', 'Maliyet (₺)', 'Birim Fiyat (₺/kWh)']

        # Yılı integer'a çevir
        yearly_cost['Yıl'] = yearly_cost['Yıl'].astype(int)

        # Boş satırları filtrele
        yearly_cost = yearly_cost[(yearly_cost['Maliyet (₺)'] > 0) | (yearly_cost['Tüketim (kWh)'] > 0)]

        # Aşırı birim fiyatlı yılları filtrele (veri hatası olabilir)
        outlier_threshold = 10.0  # Makul üst sınır: 10 TL/kWh
        outliers_yearly = yearly_cost[yearly_cost['Birim Fiyat (₺/kWh)'] > outlier_threshold]

        if len(outliers_yearly) > 0:
            st.warning(f"⚠️ {len(outliers_yearly)} yıl aşırı yüksek birim fiyat nedeniyle gizlendi (>{outlier_threshold} ₺/kWh). Veri tabanını kontrol edin!")

        # Normal değerleri göster
        yearly_cost = yearly_cost[yearly_cost['Birim Fiyat (₺/kWh)'] <= outlier_threshold]

        # Yıla göre ters sıralama (yeniden eskiye: 2025 → 2020)
        yearly_cost = yearly_cost.sort_values('Yıl', ascending=False)

        # Boş veri kontrolü
        if len(yearly_cost) == 0:
            st.warning("⚠️ Gösterilecek veri bulunamadı.")
        else:
            st.dataframe(yearly_cost.style.format({
            'Tüketim (kWh)': '{:,.0f}',
            'Maliyet (₺)': '₺{:,.2f}',
            'Birim Fiyat (₺/kWh)': '₺{:.2f}'
        }), width='stretch')

        # Maliyet artış analizi
        if len(yearly_cost) > 1:
            st.subheader("📈 Yıllık Artış Oranları")

            yearly_cost_sorted = yearly_cost.sort_values('Yıl')
            growth_rates = yearly_cost_sorted['Maliyet (₺)'].pct_change() * 100

            for idx in range(1, len(yearly_cost_sorted)):
                year = yearly_cost_sorted.iloc[idx]['Yıl']
                rate = growth_rates.iloc[idx]

                if rate > 0:
                    st.error(f"**{int(year)} yılında** bir önceki yıla göre **%{rate:.1f}** artış")
                else:
                    st.success(f"**{int(year)} yılında** bir önceki yıla göre **%{abs(rate):.1f}** azalış")

        # Tarife kategorileri bilgilendirmesi
        st.subheader("📋 Tarife Kategorileri ve Birim Fiyatlar")

        st.info("""
        ### Maliyet Hesaplama Yöntemi

        Sistemimiz, enerji maliyetlerini **tarife kategorilerine göre** hesaplar. Her kategori için
        EPDK (Enerji Piyasası Düzenleme Kurumu) tarafından belirlenen farklı birim fiyatlar uygulanır.

        **Kullanılan Tarife Kategorileri:**

        - **4AG (Alçak Gerilim)** - Evler ve küçük işletmeler için
        - **4OG (Orta Gerilim)** - Sanayi ve büyük işletmeler için
        - **URT (Üretim)** - Enerji üretim tesisleri için
        - **KAG/KOG (Kamu)** - Kamu kurumları için
        - **Diğer Kategoriler** - Özel durumlar için

        Her kategorinin tüketimi kendi birim fiyatı ile çarpılarak toplam maliyet hesaplanır.
        Bu sayede **gerçek maliyetlere** en yakın tahminler elde edilir.

        **Not:** Birim fiyatlar düzenli olarak güncellenmekte ve veritabanından otomatik olarak alınmaktadır.
        """)

        # Tarife kategorileri pasta grafiği
        fig_pie = visualizer.plot_tariff_categories_pie(df)
        st.plotly_chart(fig_pie, use_container_width=True)

    # ========================
    # TAHMİNLER
    # ========================
    elif menu == "Tahminler":
        st.header("🔮 Gelecek Tahminleri")

        # Model eğitimi
        with st.spinner('🤖 Machine Learning modeli eğitiliyor... Bu birkaç saniye sürebilir.'):
            predictor, metrics = train_prediction_model(df)

        # Eğitim hatası kontrolü
        if metrics and 'error' in metrics:
            st.error(f"❌ Model eğitilemedi: {metrics['error']}")
            st.warning("Daha fazla veri gerekiyor. Lütfen veritabanına daha fazla kayıt ekleyin.")
        elif metrics:
            st.success("✅ Model başarıyla eğitildi!")

            # Model performans metrikleri
            st.subheader("📊 Model Performansı")

            # Seçilen model (sade gösterim)
            if 'best_model' in metrics:
                st.info(f"🤖 **Kullanılan Model:** {metrics['best_model']}")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    label="Doğruluk (R² Score)",
                    value=f"{metrics['consumption_r2']:.3f}",
                    help="1'e yakın olması daha iyi (maksimum 1)"
                )

            with col2:
                st.metric(
                    label="Ortalama Hata",
                    value=f"{metrics['consumption_mae']:,.0f} kWh",
                    help="Ortalama mutlak hata"
                )

            with col3:
                st.metric(
                    label="Eğitim Verisi",
                    value=f"{metrics['training_samples']} ay",
                    help="ML modelinin eğitildiği toplam ay sayısı"
                )

            
            # Tahmin parametreleri
            st.subheader("🎯 Tahmin Ayarları")
            
            months_ahead = st.slider(
                "Kaç ay ilerisi için tahmin yapalım?",
                min_value=1,
                max_value=12,
                value=6,
                help="1 ile 12 ay arasında seçim yapabilirsiniz"
            )
            
            if st.button("🔮 Tahmin Yap", type="primary"):
                with st.spinner('Tahminler hesaplanıyor...'):
                    predictions = predictor.predict_future(months_ahead=months_ahead)
                
                if predictions is not None:
                    # Tahmin grafiği
                    st.subheader("📈 Tahmin Grafiği")
                    fig_pred = visualizer.plot_future_predictions(predictions)
                    st.plotly_chart(fig_pred, use_container_width=True)
                    
                    # Tahmin tablosu
                    st.subheader("📋 Tahmin Detayları")
                    
                    # Tablo formatını düzenle
                    predictions_display = predictions.copy()
                    predictions_display.columns = ['Tarih', 'Tahmini Tüketim (kWh)', 'Tahmini Maliyet (TL)']
                    
                    st.dataframe(predictions_display.style.format({
                        'Tahmini Tüketim (kWh)': '{:,.2f}',
                        'Tahmini Maliyet (TL)': '₺{:,.2f}'
                    }), use_container_width=True)
                    
                    # Özet bilgi
                    total_pred_consumption = predictions['Tahmini_Tuketim_kWh'].sum()
                    total_pred_cost = predictions['Tahmini_Maliyet_TL'].sum()
                    
                    st.info(f"""
                    **Toplam Tahmin ({months_ahead} ay):**
                    - Beklenen Tüketim: {total_pred_consumption:,.0f} kWh
                    - Beklenen Maliyet: ₺{total_pred_cost:,.2f}
                    """)
                    
                    # CSV olarak indirme
                    csv = predictions_display.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 Tahminleri İndir (CSV)",
                        data=csv,
                        file_name=f"enerji_tahminleri_{months_ahead}_ay.csv",
                        mime="text/csv"
                    )
        else:
            st.error("❌ Model eğitilemedi. Lütfen veri kalitesini kontrol edin.")
    
    # ========================
    # DETAYLI RAPORLAR
    # ========================
    elif menu == "Detaylı Raporlar":
        st.header("📊 Detaylı Raporlar ve Veri Analizi")
        
        # Rapor türü seçimi
        report_type = st.selectbox(
            "Rapor Türü Seçin",
            ["Aylık Detay Raporu", "Yıllık Özet Raporu"]
        )
        
        if report_type == "Aylık Detay Raporu":
            st.subheader("📅 Aylık Detay Raporu")

            # Unique term bazında hesaplama
            df_unique = df.drop_duplicates(subset=['accrual_term_id'])

            # term_total_cost varsa onu kullan
            cost_column = 'term_total_cost' if 'term_total_cost' in df_unique.columns else 'amount'

            monthly_detail = df_unique.groupby(['year', 'month']).agg({
                'total_consumption': 'sum',
                cost_column: 'sum'
            }).reset_index()

            # Tarih sütunu oluştur (YYYY-MM formatında)
            monthly_detail['Tarih'] = monthly_detail.apply(
                lambda row: f"{int(row['year'])}-{int(row['month']):02d}",
                axis=1
            )

            # Birim fiyat hesapla - sıfıra bölmeyi önle, 2 ondalık yuvarlama
            monthly_detail['unit_price'] = monthly_detail.apply(
                lambda row: round(row[cost_column] / row['total_consumption'], 2) if row['total_consumption'] > 0 else 0,
                axis=1
            )

            # Float hassasiyet hatalarını düzelt
            monthly_detail['total_consumption'] = monthly_detail['total_consumption'].round(2)
            monthly_detail[cost_column] = monthly_detail[cost_column].round(2)

            # Kolonları yeniden düzenle
            monthly_detail = monthly_detail[['Tarih', 'total_consumption', cost_column, 'unit_price']]
            monthly_detail.columns = ['Tarih', 'Tüketim (kWh)', 'Maliyet (₺)', 'Birim Fiyat (₺/kWh)']

            # Boş kayıtları filtrele
            monthly_detail = monthly_detail[(monthly_detail['Tüketim (kWh)'] > 0) | (monthly_detail['Maliyet (₺)'] > 0)]

            # Aşırı birim fiyatlı ayları filtrele (veri hatası olabilir)
            outlier_threshold = 10.0  # Makul üst sınır: 10 TL/kWh
            outliers = monthly_detail[monthly_detail['Birim Fiyat (₺/kWh)'] > outlier_threshold]

            if len(outliers) > 0:
                st.warning(f"⚠️ {len(outliers)} ay aşırı yüksek birim fiyat nedeniyle gizlendi (>{outlier_threshold} ₺/kWh). Veri tabanını kontrol edin!")

            # Normal değerleri göster
            monthly_detail = monthly_detail[monthly_detail['Birim Fiyat (₺/kWh)'] <= outlier_threshold]

            # Tarihe göre kronolojik sıralama (karşılaştırma için)
            monthly_detail_sorted = monthly_detail.sort_values('Tarih', ascending=True)

            # 1️⃣ Bir önceki aya göre değişim hesapla
            monthly_detail_sorted['Önceki Ay Tüketim'] = monthly_detail_sorted['Tüketim (kWh)'].shift(1)
            monthly_detail_sorted['Değişim %'] = monthly_detail_sorted.apply(
                lambda row: round(((row['Tüketim (kWh)'] - row['Önceki Ay Tüketim']) / row['Önceki Ay Tüketim'] * 100), 1)
                if pd.notna(row['Önceki Ay Tüketim']) and row['Önceki Ay Tüketim'] > 0 else None,
                axis=1
            )

            # Ters sıralama (yeniden eskiye: 2025 → 2020)
            monthly_detail_display = monthly_detail_sorted.sort_values('Tarih', ascending=False)

            # Gösterim için kolonları düzenle
            display_cols = ['Tarih', 'Tüketim (kWh)', 'Maliyet (₺)', 'Birim Fiyat (₺/kWh)', 'Değişim %']
            monthly_detail_display = monthly_detail_display[display_cols]

            # Tablo gösterimi
            st.dataframe(monthly_detail_display.style.format({
                'Tüketim (kWh)': '{:,.0f}',
                'Maliyet (₺)': '₺{:,.2f}',
                'Birim Fiyat (₺/kWh)': '₺{:.2f}',
                'Değişim %': lambda x: f'+{x:.1f}%' if pd.notna(x) and x > 0 else (f'{x:.1f}%' if pd.notna(x) else '-')
            }).applymap(
                lambda x: 'color: red' if isinstance(x, str) and '+' in x else ('color: green' if isinstance(x, str) and x not in ['-', 'nan'] and float(x.replace('%','')) < 0 else ''),
                subset=['Değişim %']
            ), width='stretch', height=600)
            
            # CSV indirme
            csv = monthly_detail_display.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                "📥 Aylık Raporu İndir (CSV)",
                data=csv,
                file_name="aylik_detay_raporu.csv",
                mime="text/csv"
            )

            # 2️⃣ TOP 5 / BOTTOM 5 ANALİZİ
            st.subheader("🏆 En Yüksek ve En Düşük Tüketim Ayları")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### 📈 En Yüksek 5 Ay")
                top5 = monthly_detail_sorted.nlargest(5, 'Tüketim (kWh)')[['Tarih', 'Tüketim (kWh)', 'Maliyet (₺)']]
                top5.index = range(1, len(top5) + 1)
                st.dataframe(top5.style.format({
                    'Tüketim (kWh)': '{:,.0f}',
                    'Maliyet (₺)': '₺{:,.2f}'
                }), width='stretch')

            with col2:
                st.markdown("##### 📉 En Düşük 5 Ay")
                bottom5 = monthly_detail_sorted.nsmallest(5, 'Tüketim (kWh)')[['Tarih', 'Tüketim (kWh)', 'Maliyet (₺)']]
                bottom5.index = range(1, len(bottom5) + 1)
                st.dataframe(bottom5.style.format({
                    'Tüketim (kWh)': '{:,.0f}',
                    'Maliyet (₺)': '₺{:,.2f}'
                }), width='stretch')

            # 3️⃣ ÇEYREK YIL (QUARTERLY) ÖZETİ
            st.subheader("📅 Çeyrek Yıl Özeti")

            # Quarter hesapla
            quarterly_data = monthly_detail_sorted.copy()
            quarterly_data['Yıl'] = quarterly_data['Tarih'].apply(lambda x: int(x.split('-')[0]))
            quarterly_data['Ay'] = quarterly_data['Tarih'].apply(lambda x: int(x.split('-')[1]))
            quarterly_data['Çeyrek_No'] = quarterly_data['Ay'].apply(lambda m: ((m - 1) // 3) + 1)

            # Çeyrek bazında grupla (Yıl ve Çeyrek_No ile)
            quarterly_summary = quarterly_data.groupby(['Yıl', 'Çeyrek_No']).agg({
                'Tüketim (kWh)': 'sum',
                'Maliyet (₺)': 'sum'
            }).reset_index()

            # Çeyrek string formatı oluştur (2025 Q1, 2025 Q2, vb.)
            quarterly_summary['Çeyrek'] = quarterly_summary.apply(
                lambda row: f"{int(row['Yıl'])} Q{int(row['Çeyrek_No'])}",
                axis=1
            )

            # Aylık ortalama hesapla
            quarterly_summary['Aylık Ort. Tüketim'] = quarterly_summary['Tüketim (kWh)'] / 3

            # Doğru sıralama: Yıl azalan, Çeyrek artan (2025 Q1, Q2, Q3, Q4, 2024 Q1, Q2, ...)
            quarterly_summary = quarterly_summary.sort_values(['Yıl', 'Çeyrek_No'], ascending=[False, True])

            # Gösterim için kolonları düzenle
            quarterly_display = quarterly_summary[['Çeyrek', 'Tüketim (kWh)', 'Maliyet (₺)', 'Aylık Ort. Tüketim']]

            st.dataframe(quarterly_display.style.format({
                'Tüketim (kWh)': '{:,.0f}',
                'Maliyet (₺)': '₺{:,.2f}',
                'Aylık Ort. Tüketim': '{:,.0f}'
            }), width='stretch')
        
        elif report_type == "Yıllık Özet Raporu":
            st.subheader("📊 Yıllık Özet Raporu")

            # Unique term bazında hesaplama
            df_unique = df.drop_duplicates(subset=['accrual_term_id'])

            # term_total_cost varsa onu kullan
            cost_column = 'term_total_cost' if 'term_total_cost' in df_unique.columns else 'amount'

            yearly_summary = df_unique.groupby('year').agg({
                'total_consumption': ['sum', 'mean', 'min', 'max'],
                cost_column: ['sum', 'mean']
            }).reset_index()

            yearly_summary.columns = ['Yıl', 'Toplam Tüketim', 'Ort. Tüketim',
                                     'Min Tüketim', 'Max Tüketim', 'Toplam Maliyet', 'Ort. Maliyet']

            # Boş kayıtları filtrele
            yearly_summary = yearly_summary[yearly_summary['Toplam Tüketim'] > 0]

            st.dataframe(yearly_summary.style.format({
                'Toplam Tüketim': '{:,.0f} kWh',
                'Ort. Tüketim': '{:,.0f} kWh',
                'Min Tüketim': '{:,.0f} kWh',
                'Max Tüketim': '{:,.0f} kWh',
                'Toplam Maliyet': '₺{:,.2f}',
                'Ort. Maliyet': '₺{:,.2f}'
            }), use_container_width=True)

    # Veri Yenileme Butonu
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Verileri Yenile", use_container_width=True):
        # Cache'leri temizle
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("✅ Veriler yenilendi! Sayfa yeniden yükleniyor...")
        st.rerun()

    # Footer - Minimal
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
        <div style='text-align: center; color: #6c757d; font-size: 0.85rem; padding: 1rem 0;'>
            <div style='font-weight: 600; margin-bottom: 0.5rem;'>Enerji Analiz Sistemi v2.0</div>
            <div style='font-size: 0.75rem;'>Geliştirici: Ece Erdem</div>
            <div style='font-size: 0.75rem;'>Şirket: Nar Sistem Enerji</div>
        </div>
    """, unsafe_allow_html=True)


# Uygulamayı çalıştır
if __name__ == "__main__":
    main()