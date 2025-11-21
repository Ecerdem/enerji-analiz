# Enerji Tüketim Analiz Sistemi - Claude Code Rules

## PROJE AÇIKLAMASI
Sen bir enerji tüketim analiz ve tahmin platformu üzerinde çalışıyorsun. Bu Nar Sistem Enerji için geliştirilmiş Python/Streamlit tabanlı bir web uygulaması.

**Önemli:** Tüm kullanıcı arayüzü ve çıktılar TÜRKÇE olmalı. Kod içi yorumlar ve docstring'ler Türkçe yazılmalı.

## TEMEL TEKNOLOJİLER
- **Framework:** Streamlit 1.28.0 (web UI)
- **Veri:** Pandas 2.1.0, NumPy 1.25.0
- **Grafik:** Plotly 5.17.0 (sadece graph_objects kullan, express değil)
- **ML:** scikit-learn 1.3.0 (LinearRegression)
- **Python:** 3.8+

## MİMARİ - SEPARATION OF CONCERNS

Her dosya tek sorumluluk taşır, bunu ASLA bozmayın:

```
app.py              → Sadece Streamlit UI ve kullanıcı etkileşimi
config.py           → Sadece sabitler ve yapılandırma (Config sınıfı)
data_processor.py   → Sadece veri yükleme/temizleme/birleştirme (EnergyDataProcessor)
predictor.py        → Sadece ML modelleme ve tahminler (EnergyPredictor)
visualizer.py       → Sadece Plotly grafik oluşturma (EnergyVisualizer)
```

**Kural:** Grafik kodu `visualizer.py`'de, veri işleme `data_processor.py`'de olmalı. Asla karıştırma!

## KODLAMA KURALLARI

### İsimlendirme
```python
# Class isimleri: PascalCase
class EnergyDataProcessor:
    pass

# Fonksiyon/method: snake_case
def load_data():
    pass

# Sabitler: UPPER_SNAKE_CASE (config.py'de)
VAT_RATE = 0.20
DATA_FOLDER = "data"

# Private method: _snake_case
def _get_season(month):
    pass
```

### Docstring (ZORUNLU - Türkçe)
```python
def merge_data(self) -> pd.DataFrame:
    """
    Tüm CSV tablolarını birleştir ve analiz için tek DataFrame oluştur.

    Returns:
        Birleştirilmiş ve işlenmiş DataFrame
    """
```

### Type Hints (ZORUNLU)
```python
def calculate_cost(amount: float, vat_rate: float) -> float:
    return amount * (1 + vat_rate)
```

## VERİ İŞLEME KURALLARI - KRİTİK

### 1. Tarih Formatı
```python
# Input formatı: YYYYMMDDHHmmss (örn: 20250226141640)
df['term_date'] = pd.to_datetime(
    df['term_date'],
    format='%Y%m%d%H%M%S',
    errors='coerce'  # ZORUNLU - hatalı tarihleri NaT yap
)
```

### 2. Veri Temizleme (ZORUNLU)
```python
# Sıfır ve negatif değerleri temizle
df['amount'] = df['amount'].clip(lower=0)

# NaN kontrolü
df = df[df['column'].notna()]

# Duplicates - ÇOK ÖNEMLİ!
df_unique = df.drop_duplicates(subset=['accrual_term_id'])
```

### 3. Veri İlişkileri (Ezbere Bil)
```
bi_accruals.id = bi_accrual_terms.accrual_id
bi_accrual_terms.id = bi_accrual_fees.accrual_term_id
bi_accrual_fees.id = bi_accrual_fee_consumptions.accrual_fee_id
```

**Merge Kuralı:** INNER join kullan, left join değil (gereksiz kayıtları elemek için)

```python
df_merged = pd.merge(
    df1, df2,
    left_on='id',
    right_on='accrual_id',
    how='inner',  # INNER zorunlu
    suffixes=('', '_term')
)
```

### 4. Hesaplamalar (Formüller)
```python
# KDV ve toplam hesaplama
total_amount = amount * count  # count boşsa 1 varsay
total_vat = total_amount * 0.20  # %20 KDV
grand_total = total_amount + total_vat

# Birim fiyat - SIFIRA BÖLME KONTROLÜ ZORUNLU
if consumption > 0:
    unit_price = cost / consumption
else:
    unit_price = 0
```

## GÖRSELLEŞTİRME KURALLARI

### 1. Plotly - SADECE graph_objects
```python
import plotly.graph_objects as go
# plotly.express KULLANMA!

fig = go.Figure()
fig.add_trace(go.Scatter(...))
```

### 2. Grafik Standardı
```python
fig = go.Figure()

# Hover template ZORUNLU - Türkçe
fig.add_trace(go.Scatter(
    x=data['date'],
    y=data['consumption'],
    hovertemplate='<b>Tarih:</b> %{x}<br>' +
                  '<b>Tüketim:</b> %{y:,.0f} kWh<br>' +
                  '<extra></extra>'
))

fig.update_layout(
    title='Aylık Tüketim Trendi',  # Türkçe
    xaxis_title='Tarih',  # Türkçe
    yaxis_title='Tüketim (kWh)',  # Türkçe
    template='plotly_white',  # ZORUNLU
    height=500,
    hovermode='x unified'
)
```

### 3. Renk Şeması (Config'den Al)
```python
# visualizer.py içinde
self.color_scheme = {
    'primary': '#1f77b4',    # Mavi - normal veriler
    'danger': '#d62728',     # Kırmızı - artışlar, yüksek değerler
    'success': '#2ca02c',    # Yeşil - azalışlar, olumlu
    'warning': '#ff9800',    # Turuncu - KDV, uyarılar
    'info': '#17a2b8'        # Açık mavi - bilgi
}
```

### 4. Duplicate Prevention (ÇOK ÖNEMLİ!)
```python
# Her grafik için ZORUNLU
df_unique = df.drop_duplicates(subset=['accrual_term_id'])

# Sonra gruplama yap
monthly = df_unique.groupby(['year', 'month']).agg({
    'total_consumption': 'sum',
    'grand_total': 'sum'
}).reset_index()
```

### 5. Para Formatı (Türkçe)
```python
# Sayı formatı: binlik ayırıcı + 2 ondalık
value = 12345.67
formatted = f"₺{value:,.2f}"  # ₺12,345.67

# Hover template'de
hovertemplate='<b>Maliyet:</b> ₺%{y:,.2f}<br>'
```

## STREAMLIT KURALLARI

### 1. Caching (ZORUNLU)
```python
@st.cache_data  # Veri döndüren fonksiyonlar için
def load_and_process_data():
    processor = EnergyDataProcessor()
    processor.load_data()
    return processor.get_processed_data()

@st.cache_resource  # Model/obje döndüren fonksiyonlar için
def train_model(df):
    predictor = EnergyPredictor()
    predictor.train_models(df)
    return predictor
```

### 2. Kullanıcı Bildirimleri (Türkçe + Emoji)
```python
st.success("✅ Model başarıyla eğitildi!")
st.error("❌ Veri yüklenemedi!")
st.warning("⚠️ Yüksek tüketim tespit edildi!")
st.info("ℹ️ Veriler yükleniyor...")

with st.spinner('📂 Veriler yükleniyor...'):
    data = load_data()
```

### 3. Layout
```python
# Sayfa config
st.set_page_config(
    page_title="Enerji Analiz Sistemi",
    page_icon="⚡",
    layout="wide",  # ZORUNLU - geniş ekran
    initial_sidebar_state="expanded"
)

# Kolonlar
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Toplam Tüketim", f"{consumption:,.0f} kWh")
```

## MACHINE LEARNING KURALLARI

### Model Parametreleri (config.py'den)
```python
# Sabitler
ML_TEST_SPLIT_RATIO = 0.2
ML_RANDOM_STATE = 42
ML_MIN_TRAINING_SAMPLES = 10

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,  # %20 test
    random_state=42  # Reproducibility
)
```

### Feature Engineering
```python
# Tarih özellikleri
features = {
    'year': date.year,
    'month': date.month,
    'quarter': (date.month - 1) // 3 + 1,
    'season': get_season(date.month),  # 1-4
    'months_from_start': calculated_value
}
```

### Mevsim Tanımı (Ezber)
```python
def _get_season(self, month: int) -> int:
    """Aydan mevsim bilgisi çıkar (1-4)"""
    if month in [3, 4, 5]:
        return 1  # İlkbahar
    elif month in [6, 7, 8]:
        return 2  # Yaz
    elif month in [9, 10, 11]:
        return 3  # Sonbahar
    else:
        return 4  # Kış (12, 1, 2)
```

## HATA YÖNETİMİ

### Veri Yükleme
```python
try:
    df = pd.read_csv(file_path)
    print(f"✅ {filename} yüklendi: {len(df)} kayıt")
    return True
except FileNotFoundError as e:
    print(f"❌ Hata: Dosya bulunamadı - {e}")
    return False
except Exception as e:
    print(f"❌ Beklenmeyen hata: {e}")
    return False
```

### Veri Doğrulama
```python
# DataFrame boşluk kontrolü
if df is None or len(df) == 0:
    st.error("❌ Veri bulunamadı!")
    return None

# Sütun varlık kontrolü
if 'required_column' not in df.columns:
    st.error("❌ Gerekli sütun bulunamadı!")
    return None

# Sıfıra bölme kontrolü
unit_price = cost / consumption if consumption > 0 else 0
```

## KRİTİK KURALLAR (ASLA UNUTMA!)

### 1. Duplicate Prevention
```python
# GRAFİKLERDE ZORUNLU - Her term bir kez sayılmalı
df_unique = df.drop_duplicates(subset=['accrual_term_id'])
```

### 2. Sıfıra Bölme
```python
# HER BÖLME İŞLEMİNDE
result = numerator / denominator if denominator > 0 else 0
```

### 3. Tarih Parse
```python
# HER ZAMAN errors='coerce'
pd.to_datetime(df['date'], format='%Y%m%d%H%M%S', errors='coerce')
```

### 4. Inner Join
```python
# Left join DEĞİL, inner join
pd.merge(..., how='inner')
```

### 5. Negatif Değer Temizleme
```python
# Tüketim ve maliyet negatif olamaz
df['amount'] = df['amount'].clip(lower=0)
```

### 6. Config Kullanımı
```python
# Hard-coded değer YASAK
# ❌ YANLIŞ
vat = amount * 0.20

# ✅ DOĞRU
from config import Config
vat = amount * Config.VAT_RATE
```

### 7. Türkçe Arayüz
```python
# UI'da Türkçe ZORUNLU
st.title("⚡ Enerji Tüketim Analiz Sistemi")  # ✅
st.title("Energy Analysis System")  # ❌
```

## PERFORMANS OPTİMİZASYONU

### Pandas Optimizasyonu
```python
# ✅ İYİ - Önce duplicate'leri temizle
df_unique = df.drop_duplicates(subset=['accrual_term_id'])
result = df_unique.groupby('year').sum()

# ❌ KÖTÜ - Yavaş
result = df.groupby('year').apply(lambda x: x.drop_duplicates().sum())
```

### Streamlit Cache
```python
# Veri yükleme ve model eğitimi ZORUNLU cache'lenmeli
@st.cache_data
def load_data():
    pass

@st.cache_resource
def train_model(df):
    pass
```

## ÖZEL DURUMLAR

### term_grand_total vs grand_total
```python
# İki versiyonda da çalışabilmeli
cost_column = 'term_grand_total' if 'term_grand_total' in df.columns else 'grand_total'
total_cost = df[cost_column].sum()
```

### Boş Grafik Durumu
```python
if len(data) == 0:
    fig = go.Figure()
    fig.add_annotation(
        text="Gösterilecek veri bulunamadı",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=20, color="gray")
    )
    return fig
```

## YASAKLAR

1. ❌ `plotly.express` kullanmak (sadece `graph_objects`)
2. ❌ Hard-coded sabitler (config.py kullan)
3. ❌ İngilizce UI metinleri (Türkçe zorunlu)
4. ❌ Sıfıra bölme kontrolsüz bölme işlemi
5. ❌ `errors='coerce'` olmadan tarih parse
6. ❌ Duplicate kontrolü olmadan gruplama
7. ❌ Left join (sadece inner join)
8. ❌ Modül sorumlulukları karıştırmak
9. ❌ Cache olmadan ağır işlemler
10. ❌ Kullanıcıya İngilizce hata mesajı

## YENİ KOD YAZARKEN

1. **Hangi dosyada?** Separation of concerns kontrolü yap
2. **Docstring var mı?** Türkçe docstring ekle
3. **Type hints var mı?** Tip belirtme ekle
4. **Config kullanıyor mu?** Hard-coded sabitleri config'e taşı
5. **Duplicate kontrol var mı?** `drop_duplicates` ekle
6. **Sıfıra bölme var mı?** Kontrol ekle
7. **Tarih parse var mı?** `errors='coerce'` ekle
8. **Grafik mi?** `graph_objects` kullan, `hovertemplate` ekle
9. **Türkçe mi?** Tüm UI metinleri Türkçe yap
10. **Cache gerekli mi?** `@st.cache_data` veya `@st.cache_resource` ekle

## HIZLI REFERANS

```python
# Standart veri temizleme pipeline
df = pd.read_csv(file_path)
df['date'] = pd.to_datetime(df['date'], format='%Y%m%d%H%M%S', errors='coerce')
df['amount'] = df['amount'].clip(lower=0)
df = df[df['amount'].notna()]
df_unique = df.drop_duplicates(subset=['accrual_term_id'])

# Standart grafik oluşturma
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['date'],
    y=df['value'],
    mode='lines+markers',
    hovertemplate='<b>Tarih:</b> %{x}<br><b>Değer:</b> %{y:,.2f}<br><extra></extra>'
))
fig.update_layout(
    title='Grafik Başlığı',
    xaxis_title='X Ekseni',
    yaxis_title='Y Ekseni',
    template='plotly_white',
    height=500
)

# Standart Streamlit cache
@st.cache_data
def load_data():
    return pd.read_csv('data.csv')
```

---

**SONUÇ:** Bu proje veri analizi ve görselleştirme odaklı. Temel prensipler: temiz veri, doğru hesaplama, anlaşılır Türkçe arayüz, hızlı performans. Her değişiklikte bu prensipleri koru!
