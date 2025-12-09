# Enerji Tüketim Analiz Sistemi - Claude Code Rules

## PROJE AÇIKLAMASI
Sen bir enerji tüketim analiz ve tahmin platformu üzerinde çalışıyorsun. Bu Nar Sistem Enerji için geliştirilmiş Python/Streamlit tabanlı bir web uygulaması.

**Önemli:** Tüm kullanıcı arayüzü ve çıktılar TÜRKÇE olmalı. Kod içi yorumlar ve docstring'ler Türkçe yazılmalı.

## TEMEL TEKNOLOJİLER
- **Framework:** Streamlit 1.28.0 (web UI)
- **Veri:** Pandas 2.1.0, NumPy 1.25.0
- **Grafik:** Plotly 5.17.0
- **ML:** scikit-learn 1.3.0 (Random Forest Regressor)
- **Veritabanı:** PostgreSQL 12+ (psycopg2-binary 2.9.9, SQLAlchemy 2.0.23)
- **Python:** 3.8+

## MİMARİ - SEPARATION OF CONCERNS

Her dosya tek sorumluluk taşır, bunu ASLA bozmayın:

```
app.py              → Sadece Streamlit UI ve kullanıcı etkileşimi
database.py         → PostgreSQL bağlantı yönetimi (DatabaseManager - Singleton)
data_processor.py   → Sadece veri yükleme/temizleme/birleştirme (EnergyDataProcessor)
predictor.py        → Sadece ML modelleme ve tahminler (EnergyPredictor)
visualizer.py       → Sadece Plotly grafik oluşturma (EnergyVisualizer)
```

**ÖNEMLİ:** `config.py` artık kullanılmıyor. Sabitler ilgili modüllerde tanımlanmıştır.

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

### 3. Veri Kaynağı ve İlişkileri

**VERİTABANI (PostgreSQL) - Birincil Kaynak:**
```
Tablolar:
- bi_accruals (6,067 kayıt)           → Fatura bilgileri
- bi_accrual_terms (11,027 kayıt)     → Dönem bilgileri
- bi_accrual_fees (14,549 kayıt)      → Ücret detayları
- bi_accrual_fee_consumptions (33,352)→ Tüketim detayları

İlişkiler:
bi_accruals.id = bi_accrual_terms.accrual_id
bi_accrual_terms.id = bi_accrual_fees.accrual_term_id
bi_accrual_fees.id = bi_accrual_fee_consumptions.accrual_fee_id
```

**Merge Kuralı:** İlk iki birleştirme INNER join, son birleştirme LEFT join (consumptions opsiyonel)

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

## VERİTABANI KURALLARI

### PostgreSQL Bağlantısı (.env dosyası)
```bash
# .env dosyası (GIT'e eklenmez!)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=enerji_analiz_db
DB_USER=postgres
DB_PASSWORD=your_password
USE_DATABASE=True
```

**UYARI:** `.env` dosyası `.gitignore`'a eklenmiş olmalı!

### Singleton Pattern (DatabaseManager)
```python
_db_manager = None

def get_database_manager():
    """Singleton DB instance - tek bir bağlantı havuzu"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
```

### Connection Pooling (SQLAlchemy)
```python
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# Şifre encoding (özel karakterler için)
password = quote_plus(os.getenv('DB_PASSWORD'))

engine = create_engine(
    f"postgresql://{user}:{password}@{host}:{port}/{db}",
    pool_size=5,           # Havuz boyutu
    max_overflow=10,       # Maksimum ek bağlantı
    pool_timeout=30,       # 30 saniye timeout
    pool_recycle=3600      # 1 saat sonra yenile
)
```

## GÖRSELLEŞTİRME KURALLARI

### 1. Plotly Kullanımı
```python
import plotly.graph_objects as go

# visualizer.py içinde grafik oluşturma metodları
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

### Model: Random Forest Regressor
```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# ZORUNLU Hiperparametreler
model = RandomForestRegressor(
    n_estimators=100,      # 100 ağaç
    max_depth=10,          # Overfitting önleme
    random_state=42,       # Tekrarlanabilirlik
    n_jobs=-1              # Tüm CPU core'ları kullan
)

# Feature scaling (ZORUNLU)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y,
    test_size=0.2,  # %20 test
    random_state=42  # Reproducibility
)
```

### 7 Feature (Değiştirme - Model bu feature'larla eğitildi!)
```python
features = [
    'year',              # Yıl (2020-2025)
    'month',             # Ay (1-12)
    'months_from_start', # Time series feature
    'season',            # Mevsim (1-4)
    'quarter',           # Çeyrek (1-4)
    'is_summer',         # Binary (0/1)
    'is_winter'          # Binary (0/1)
]
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

### 6. Pandas sort_values() Kullanımı
```python
# ❌ YANLIŞ - Tip hatası verebilir
df = df.sort_values('Yıl', ascending=False)

# ✅ DOĞRU - 'by' parametresini açıkça belirt
df = df.sort_values(by='Yıl', ascending=False)
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

1. ❌ İngilizce UI metinleri (Türkçe zorunlu)
2. ❌ Sıfıra bölme kontrolsüz bölme işlemi
3. ❌ `errors='coerce'` olmadan tarih parse
4. ❌ Duplicate kontrolü olmadan gruplama
5. ❌ `sort_values()` kullanırken 'by' parametresi belirtmemek
6. ❌ Kullanılmayan import'lar (kod temizliği)
7. ❌ Modül sorumlulukları karıştırmak
8. ❌ Cache olmadan ağır işlemler (veri yükleme, ML)
9. ❌ Veritabanı şifrelerini kodda yazmak (.env kullan)
10. ❌ Random Forest hiperparametrelerini değiştirmek (n_estimators=100, max_depth=10)

## YENİ KOD YAZARKEN - CHECKLIST

1. **Hangi dosyada?** Separation of concerns kontrolü yap
2. **Docstring var mı?** Türkçe docstring ekle
3. **Type hints var mı?** Tip belirtme ekle
4. **Duplicate kontrol var mı?** `drop_duplicates(subset=['accrual_term_id'])` ekle
5. **Sıfıra bölme var mı?** Kontrol ekle (`if denominator > 0`)
6. **Tarih parse var mı?** `errors='coerce'` ekle
7. **sort_values() kullanıyor mu?** `by` parametresi belirt
8. **Grafik mi?** Plotly `graph_objects` kullan, `hovertemplate` ekle (Türkçe)
9. **Türkçe mi?** Tüm UI metinleri Türkçe yap
10. **Cache gerekli mi?** `@st.cache_data` (veri) veya `@st.cache_resource` (model) ekle
11. **Veritabanı kullanıyor mu?** `.env` dosyasından bilgileri oku
12. **Import temizliği?** Kullanılmayan import'ları kaldır

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

## SON DÜZELTMELER (2025-11-25)

### app.py Güncellemeleri

**1. sort_values() Tip Hataları Düzeltildi**
```python
# ÖNCESİ (Hatalı)
yearly_cost = yearly_cost.sort_values('Yıl', ascending=False)

# SONRASI (Doğru)
yearly_cost = yearly_cost.sort_values(by='Yıl', ascending=False)
```

**Düzeltilen satırlar:**
- Satır 261: `yearly_cost.sort_values(by='Yıl', ascending=False)`
- Satır 478: `monthly_detail.sort_values(by='Tarih', ascending=True)`
- Satır 595: `yearly_summary.sort_values(by='Yıl', ascending=False)`

**2. Kullanılmayan Import'lar Kaldırıldı**
```python
# ÖNCESİ
import plotly.graph_objects as go  # ❌ Kullanılmıyor
from config import Config           # ❌ Kullanılmıyor

# SONRASI
# Import'lar temizlendi - sadece kullanılanlar kaldı
```

---

**SONUÇ:** Bu proje PostgreSQL entegreli, Random Forest ML destekli bir enerji analiz platformu. Temel prensipler: temiz veri, doğru hesaplama, anlaşılır Türkçe arayüz, hızlı performans, güvenli veritabanı yönetimi. Her değişiklikte bu prensipleri koru!
