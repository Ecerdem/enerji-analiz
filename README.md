# ENERJİ TÜKETİM ANALİZ VE TAHMİN SİSTEMİ

Modern ve kullanıcı dostu bir enerji tüketim analiz platformu. PostgreSQL veritabanı ile entegre, Streamlit tabanlı web arayüzü ile enerji tüketim verilerinizi analiz edin, görselleştirin ve Machine Learning ile gelecek tahminleri yapın.

---

## 📋 İçindekiler

1. [Proje Özeti](#-proje-özeti)
2. [Hızlı Başlangıç](#-hızlı-başlangıç)
3. [Kullanılan Teknolojiler](#-kullanılan-teknolojiler)
4. [Özellikler ve Sayfalar](#-özellikler-ve-sayfalar)
5. [Machine Learning Modeli](#-machine-learning-modeli)
6. [Mimari ve Proje Yapısı](#-mimari-ve-proje-yapısı)
7. [Teknik Detaylar](#-teknik-detaylar)
8. [Sorun Giderme](#-sorun-giderme)
9. [İletişim](#-iletişim)

---

## 🎯 Proje Özeti

### Projeyi Neden Yaptık?

Günümüzde enerji dağıtım şirketleri ve enerji tedarikçileri müşterilerine tonla data tutuyor ama bu verileri anlamlı hale getirip sunacak gelişmiş analiz araçları yok. Müşteriler (hem firmalar hem de ev kullanıcıları) geçmiş tüketimlerini düzgün göremiyorlar, gelecek için tahmin yapamıyorlar, mevsimsel değişimleri anlayamıyorlar.

Bu proje, enerji sağlayıcıların müşterilerine sunabileceği profesyonel bir analiz ve tahmin platformu olarak geliştirildi. Hem müşterilere değerli bir hizmet sunuluyor, hem de müşteriler kendi tüketimlerini anlayıp bütçe planlayabiliyor.

### Veri İstatistikleri

- **Toplam Kayıt:** 12,959 işlem
- **Toplam Tüketim:** 106+ Milyon kWh
- **Toplam Maliyet:** ₺72+ Milyon
- **Tarih Aralığı:** 2020 - 2025 (5 yıl)
- **Unique Fatura:** 2,711 adet
- **Veri Kaynakları:** 4 farklı tablo (PostgreSQL)

### Temel Özellikler

✅ **5 Ana Sayfa** ile kapsamlı analiz
✅ **6 Farklı Grafik Türü** ile görselleştirme
✅ **Machine Learning (Random Forest)** ile gelecek tahmini
✅ **PostgreSQL Veritabanı** entegrasyonu
✅ **Tarife Kategorisi Bazlı** maliyet hesaplama
✅ **CSV Export** desteği
✅ **Responsive** web arayüzü

---

## 🚀 Hızlı Başlangıç

### Gereksinimler

- **Python 3.8+**
- **PostgreSQL 12+** (veritabanı için)
- **pip** paket yöneticisi

### Kurulum Adımları

#### 1. Gerekli Kütüphaneleri Yükleyin

```bash
pip install -r requirements.txt
```

**Ana Kütüphaneler:**
- streamlit==1.28.0
- pandas==2.1.0
- numpy==1.25.0
- plotly==5.17.0
- scikit-learn==1.3.0
- psycopg2-binary==2.9.9
- sqlalchemy==2.0.23
- python-dotenv==1.0.0
- openpyxl==3.1.2

#### 2. Veritabanı Bağlantısını Yapılandırın

`.env` dosyası oluşturun:

```bash
# Veritabanı bağlantı bilgileri
DB_HOST=localhost
DB_PORT=5432
DB_NAME=enerji_analiz_db
DB_USER=postgres
DB_PASSWORD=your_password

# Veri kaynağı
USE_DATABASE=True
```

**Gerekli Tablolar:**
- `bi_accruals` - Fatura bilgileri
- `bi_accrual_fees` - Ücret detayları
- `bi_accrual_terms` - Dönem bilgileri
- `bi_accrual_fee_consumptions` - Tüketim detayları

#### 3. Veritabanı Bağlantısını Test Edin

```bash
python database.py
```

#### 4. Uygulamayı Çalıştırın

```bash
streamlit run app.py
```

#### 5. Tarayıcınızda Açın

```
http://localhost:8501
```

---

## 💻 Kullanılan Teknolojiler

### Frontend & Web Arayüzü

#### **Streamlit (v1.28.0)**

**Neden Seçtik:**
- Sıfır HTML/CSS bilgisi ile profesyonel web arayüzü
- Python ile direkt entegrasyon
- Hızlı prototipleme
- Built-in cache mekanizması ile yüksek performans
- Responsive tasarım desteği

**Ne İçin Kullandık:**
- Ana uygulama arayüzü
- 5 sayfalı menü sistemi
- Kullanıcı etkileşimi (filtreler, slider)
- KPI kartları (metrics)

---

### Veri İşleme ve Analiz

#### **Pandas (v2.1.0)**

**Neden Seçtik:**
- Python'da veri analizi için endüstri standardı
- Güçlü DataFrame yapısı
- SQL benzeri işlemler (join, group by, filter)

**Ne İçin Kullandık:**
- 4 farklı veri kaynağını birleştirme (merge/join)
- Veri temizleme (null değer, duplikasyon)
- Tarih formatı dönüştürme (YYYYMMDDHHmmss → datetime)
- Aylık/yıllık gruplamalar
- Hesaplanan alanlar (total_consumption, grand_total, vb.)

#### **NumPy (v1.25.0)**

**Ne İçin Kullandık:**
- Matematiksel hesaplamalar
- İstatistiksel analizler (ortalama, medyan, standart sapma)
- Outlier tespiti (IQR metodu)
- Veri normalizasyonu

---

### Görselleştirme

#### **Plotly (v5.17.0)**

**Neden Seçtik:**
- İnteraktif grafikler (zoom, pan, hover)
- Profesyonel ve modern görünüm
- Streamlit ile mükemmel entegrasyon
- Export özelliği (PNG, SVG)
- Responsive tasarım

**Oluşturduğumuz 6 Grafik Türü:**

1. **Tüketim Trend Grafiği** - Aylık tüketim + trend çizgisi + outlier tespiti
2. **Mevsimsel Analiz Grafiği** - 4 mevsim karşılaştırması (bar chart)
3. **Maliyet Analizi Grafiği** - Aylık maliyet + trend çizgisi
4. **Yıllık Karşılaştırma Grafiği** - Dual Y-axis (tüketim + maliyet)
5. **Tarife Kategorileri Pasta Grafiği** - 4AG, 4OG, URT, KAG/KOG dağılımı
6. **Tahmin Grafiği** - Gelecek ay tahminleri (dual Y-axis)

---

### Machine Learning & Tahminleme

#### **Scikit-learn (v1.3.0)**

**Neden Seçtik:**
- Python'da ML için en popüler kütüphane
- Kullanımı kolay ve iyi dokümante edilmiş
- Çok sayıda hazır algoritma
- Model değerlendirme metrikleri

**Kullandığımız Model:**
- **Random Forest Regressor** - Ana tahmin modeli
  - n_estimators=100 (100 ağaç)
  - max_depth=10
  - random_state=42
  - n_jobs=-1 (tüm CPU core'ları kullan)

**Tahmin Özellikleri:**
- 1-12 ay arası esnek tahmin aralığı
- 7 farklı feature engineering
- Model performans göstergeleri (R² Score, MAE, MAPE)
- CSV export ile tahmin sonuçlarını indirme

---

### Veritabanı Yönetimi

#### **PostgreSQL + psycopg2-binary (v2.9.9)**

**Neden Seçtik:**
- Açık kaynak ve güçlü ilişkisel veritabanı
- Büyük veri hacimlerine uygun
- ACID compliance (veri güvenliği)

**Ne İçin Kullandık:**
- 4 tablo için veri depolama
- Connection pooling ile performans optimizasyonu
- Güvenli şifre yönetimi

#### **SQLAlchemy (v2.0.23)**

**Ne İçin Kullandık:**
- Database engine oluşturma
- Connection pooling ayarları:
  - Pool size: 5
  - Max overflow: 10
  - Pool timeout: 30s
  - Pool recycle: 1 saat

---

### Konfigürasyon ve Güvenlik

#### **python-dotenv (v1.0.0)**

**Ne İçin Kullandık:**
- Veritabanı bağlantı bilgileri
- Hassas bilgileri (şifre) koddan ayırma
- `.env` dosyası ile güvenlik
- `.gitignore` ile şifre koruması

---

## 📊 Özellikler ve Sayfalar

### 1. Ana Sayfa - Genel Özet

**Özellikler:**
- Toplam tüketim ve maliyet KPI kartları
- En yüksek/düşük tüketim ayları
- Hızlı bakış grafikleri:
  - Tüketim trend grafiği
  - Yıllık karşılaştırma

**Kullanılan Teknolojiler:**
- Streamlit metrics
- Pandas aggregation
- Plotly

---

### 2. Tüketim Analizi Sayfası

**Özellikler:**
- **Aylık Tüketim Trend Grafiği**
  - Outlier tespiti (IQR metodu)
  - Trend çizgisi
  - İnteraktif hover bilgileri
- **Mevsimsel Analiz Grafiği**
  - 4 mevsim karşılaştırması (Kış, İlkbahar, Yaz, Sonbahar)
  - Ortalama ve toplam tüketim
  - Renkli görselleştirme

**Öne Çıkan Bulgular:**
- Kış aylarında ortalama %37 daha fazla tüketim
- Yaz aylarında ortalama %17 daha fazla tüketim (klima)
- Sonbahar ayları en düşük tüketim

---

### 3. Maliyet Analizi Sayfası

**Özellikler:**
- **Aylık Maliyet Trend Grafiği** (KDV Hariç)
- **Yıllık Karşılaştırma Grafiği** (Dual Y-axis)
  - Sol eksen: Tüketim (kWh)
  - Sağ eksen: Maliyet (TL)
  - Yıl-yıl değişim oranları (%)
- **Yıllık Maliyet Özet Tablosu**
  - Yıl, Tüketim, Maliyet, Birim Fiyat (TL/kWh)
  - Outlier filtreleme (>10 TL/kWh)
- **Yıllık Artış Oranları**
  - Bir önceki yıla göre % değişim
- **Tarife Kategorileri Bilgilendirmesi**
- **Tarife Kategorileri Pasta Grafiği**
  - 4AG (Alçak Gerilim) - Evler ve küçük işletmeler
  - 4OG (Orta Gerilim) - Sanayi ve büyük işletmeler
  - URT (Üretim) - Enerji üretim tesisleri
  - KAG/KOG (Kamu) - Kamu kurumları
  - Diğer Kategoriler

**Maliyet Hesaplama Yöntemi:**
- Her tarife kategorisi için EPDK tarafından belirlenen farklı birim fiyatlar uygulanır
- Kategori dağılımına göre ağırlıklı ortalama hesaplanır
- Gerçek maliyetlere en yakın tahminler elde edilir

---

### 4. Tahminler Sayfası

**Özellikler:**
- **Machine Learning Modeli Eğitimi**
  - Random Forest Regressor
  - Otomatik cache ile hızlı yükleme
- **Model Performans Metrikleri**
  - R² Score (Doğruluk): 0.85+ (hedef: 1.00)
  - MAE (Ortalama Hata): ~180,000 kWh (%9 hata)
  - Eğitim verisi sayısı
- **Tahmin Ayarları**
  - 1-12 ay arası slider ile seçim
  - Otomatik tahmin butonu
- **Tahmin Grafiği**
  - Gelecek ay tahminleri
  - Dual Y-axis (Tüketim + Maliyet)
  - İnteraktif hover
- **Tahmin Detayları Tablosu**
  - Tarih, Tahmini Tüketim, Tahmini Maliyet
  - Toplam tahmin özeti
- **CSV Export**
  - Tahminleri indirme özelliği

**Tahmin Süreci:**
1. Geçmiş verileri Random Forest ile öğren
2. 7 feature kullanarak gelecek ayları tahmin et
3. Kategori bazlı maliyet hesapla
4. Sonuçları görselleştir ve indir

---

### 5. Detaylı Raporlar Sayfası

**Rapor Türleri:**

#### **A) Aylık Detay Raporu**
- Yıl-Ay bazında detaylı tablo
- Tüketim (kWh), Maliyet (TL), Birim Fiyat (TL/kWh)
- **Değişim %** - Bir önceki aya göre artış/azalış
- Outlier filtreleme (>10 TL/kWh)
- Renk kodlu değişim gösterimi (yeşil: azalış, kırmızı: artış)
- CSV indirme

**Ek Analizler:**
- **TOP 5 / BOTTOM 5** - En yüksek ve en düşük tüketim ayları
- **Çeyrek Yıl Özeti** - Q1, Q2, Q3, Q4 bazında gruplamalar

#### **B) Yıllık Özet Raporu**
- Yıl bazında toplam, ortalama, min, max değerler
- Tüketim ve maliyet istatistikleri
- CSV indirme

---

## 🤖 Machine Learning Modeli

### Neden Random Forest Kullanıyoruz?

#### 1. Outlier'lara Dayanıklı
Enerji verilerinde sık sık anormal tüketimler olur (tatil günleri, bakım/arıza, ekstra yük). Random Forest, 100 farklı karar ağacının ortalamasını aldığı için bu aykırı değerlerden çok etkilenmez.

#### 2. Non-Linear İlişkileri Yakalama
Enerji tüketimi doğrusal (linear) değildir:
- Kışın tüketim yaz ayının 2-3 katı olabilir
- Sıcaklık 25°C'den 35°C'ye çıkınca tüketim exponansiyel artar

Random Forest bu tip karmaşık ilişkileri modelleyebilir. Linear Regression bunu yapamaz.

#### 3. Feature Importance (Özellik Önem Sıralaması)
Random Forest, hangi faktörlerin tahminde en önemli olduğunu söyler:

**Örnek Çıktı:**
1. `month` (ay) → %35 önem
2. `season` (mevsim) → %25 önem
3. `is_winter` (kış mı?) → %15 önem
4. `months_from_start` (trend) → %12 önem
5. `is_summer` (yaz mı?) → %8 önem
6. `quarter` (çeyrek) → %3 önem
7. `year` (yıl) → %2 önem

**Sonuç:** Mevsimsellik faktörleri toplam %83 önem taşıyor!

#### 4. Overfitting'e Dayanıklı
Az veriyle çalışırken model "ezberleyebilir" (overfit). Random Forest, birden fazla ağacı rastgele örneklerle eğittiği için ezberlemez, genelleştirir.

#### 5. Hiperparametre Tuning'e Az İhtiyaç
Random Forest, varsayılan parametrelerle bile iyi sonuç verir. Projemizde kullandığımız ayarlar:
- `n_estimators=100` (100 ağaç)
- `max_depth=10` (ağaç derinliği)
- `random_state=42` (tekrarlanabilirlik)
- `n_jobs=-1` (tüm CPU core'ları kullan)

---

### Model Hangi Parametrelere Göre Tahmin Yapıyor?

**7 Ana Feature (Özellik):**

#### 1. **year** (Yıl)
```
Örnek: 2020, 2021, 2022, 2023, 2024, 2025

Amacı:
- Yıllık trend'i yakalamak
- Enerji verimliliği artışını modellemek
- Yıllık büyüme/azalma oranını öğrenmek

Örnek Pattern:
2020 → 20.5M kWh
2021 → 21.2M kWh (+3.4%)
2022 → 22.1M kWh (+4.2%)
2023 → 23.5M kWh (+6.3%)

Model öğrenir: "Her yıl yaklaşık %4-5 artış var"
```

#### 2. **month** (Ay)
```
Örnek: 1 (Ocak), 2 (Şubat), ..., 12 (Aralık)

Amacı:
- Aylık mevsimsellik
- Her ayın kendine özgü tüketim pattern'i

Örnek Pattern:
Ocak → 2.5M kWh (Yüksek - Kış)
Nisan → 1.8M kWh (Orta - İlkbahar)
Temmuz → 2.2M kWh (Yüksek - Klima)
Ekim → 1.6M kWh (Düşük - Sonbahar)

Model öğrenir: "Ocak ve Temmuz ayları genelde yüksek"
```

#### 3. **months_from_start** (Başlangıçtan Beri Geçen Ay Sayısı)
```
Örnek:
2020-01 → 0 (başlangıç)
2020-02 → 1
2020-03 → 2
...
2024-12 → 59

Amacı:
- Uzun vadeli trend'i yakalamak (time series)
- Zaman içinde artış/azalış pattern'ini modellemek

Neden Önemli:
Model şöyle öğrenir: "Her ay yaklaşık 0.008M kWh artıyor"
Bu daha hassas tahmin sağlar!
```

#### 4. **season** (Mevsim)
```
Kodlama:
1 = İlkbahar (Mart, Nisan, Mayıs)
2 = Yaz (Haziran, Temmuz, Ağustos)
3 = Sonbahar (Eylül, Ekim, Kasım)
4 = Kış (Aralık, Ocak, Şubat)

Amacı:
- Mevsimsel tüketim farklarını yakalamak
- 4 farklı enerji profili modellemek

Örnek Pattern:
İlkbahar → 1.7M kWh (Orta)
Yaz → 2.1M kWh (Yüksek - Klima)
Sonbahar → 1.5M kWh (Düşük)
Kış → 2.4M kWh (En Yüksek - Isınma)

Model öğrenir: "Kış ve yaz tüketimi yüksek, sonbahar düşük"
```

#### 5. **quarter** (Çeyrek Dönem)
```
Kodlama:
Q1 = Ocak-Şubat-Mart (1)
Q2 = Nisan-Mayıs-Haziran (2)
Q3 = Temmuz-Ağustos-Eylül (3)
Q4 = Ekim-Kasım-Aralık (4)

Amacı:
- Üç aylık dönemsel pattern'leri yakalamak
- İş döngülerini modellemek

Model öğrenir: "Q1 genelde en yüksek, Q2 en düşük"
```

#### 6. **is_summer** (Yaz Ayları mı?)
```
Kodlama:
0 = Yaz değil
1 = Yaz (Haziran, Temmuz, Ağustos)

Amacı:
- Yaz aylarının özel tüketim pattern'ini vurgulamak
- Klima kullanımını modellemek

Örnek Pattern:
Yaz Ayları Ortalama: 2.17M kWh
Diğer Aylar Ortalama: 1.85M kWh

Model öğrenir: "Yaz aylarında +17% daha fazla tüketim var"
```

#### 7. **is_winter** (Kış Ayları mı?)
```
Kodlama:
0 = Kış değil
1 = Kış (Aralık, Ocak, Şubat)

Amacı:
- Kış aylarının özel tüketim pattern'ini vurgulamak
- Isınma yükünü modellemek

Örnek Pattern:
Kış Ayları Ortalama: 2.5M kWh
Diğer Aylar Ortalama: 1.82M kWh

Model öğrenir: "Kış aylarında +37% daha fazla tüketim var"
```

---

### Model Performans Metrikleri

#### 1. R² Score (R-squared, Determination Coefficient)
```
Tanım: Modelin açıklanan varyans oranı

Yorumlama:
R² = 0.85 → %85 doğruluk
R² = 1.00 → %100 doğruluk (mükemmel)
R² = 0.00 → Model hiçbir şey öğrenmemiş

Projemdeki Sonuç:
R² = 0.87 → Çok iyi! Model varyansın %87'sini açıklıyor
```

#### 2. MAE (Mean Absolute Error)
```
Tanım: Ortalama mutlak hata

Yorumlama:
MAE = 150,000 kWh → Ortalama ±150,000 kWh hata
Düşük olması iyidir

Projemdeki Sonuç:
Aylık ortalama tüketim: 2,000,000 kWh
MAE: 180,000 kWh
Hata oranı: 180k / 2000k = %9 → Kabul edilebilir
```

#### 3. MAPE (Mean Absolute Percentage Error)
```
Tanım: Ortalama mutlak yüzde hata

Yorumlama:
MAPE = 8% → Ortalama %8 hata
MAPE < 10% → Çok iyi
MAPE < 20% → İyi
MAPE > 30% → Kötü

Projemdeki Sonuç:
MAPE ≈ 9% → Çok iyi tahmin performansı
```

---

### Tahmin Süreci Örneği: 2025 Şubat Tahmini

```python
# 1. Feature'ları hazırla:
features = {
    'year': 2025,
    'month': 2,
    'months_from_start': 61,  # (2025-2020)*12 + (2-1)
    'season': 4,  # Kış
    'quarter': 1,  # Q1
    'is_summer': 0,
    'is_winter': 1  # Evet, kış!
}

# 2. Normalize et (StandardScaler)
X_scaled = scaler.transform(features)

# 3. Random Forest tahmini
predicted_consumption = model.predict(X_scaled)
# Sonuç: 2,350,000 kWh

# 4. Maliyet hesaplama (Kategori bazlı)
# Her tarife kategorisi için ağırlıklı hesaplama:
# 4OG: %51.5 × 4.46 TL/kWh = 2.30 TL/kWh katkı
# 4AG: %27.0 × 2.14 TL/kWh = 0.58 TL/kWh katkı
# URT: %15.0 × 3.20 TL/kWh = 0.48 TL/kWh katkı
# Diğer: %6.5 × 5.00 TL/kWh = 0.33 TL/kWh katkı
# Toplam Ağırlıklı Birim Fiyat = 3.69 TL/kWh

predicted_cost = 2,350,000 × 3.69 = 8,671,500 TL
```

---

## 🏗️ Mimari ve Proje Yapısı

### Modüler Tasarım

Projeyi **6 ana modül** ile organize ettik:

```
1. app.py (26 KB)
   └─ Streamlit arayüzü
   └─ 5 sayfa yönetimi
   └─ Cache mekanizması

2. config.py (8 KB)
   └─ Merkezi ayarlar
   └─ Ortam yönetimi (Dev, Prod, Test)
   └─ Sabitler ve validasyon

3. database.py (8 KB)
   └─ PostgreSQL bağlantısı
   └─ Connection pooling
   └─ Singleton pattern

4. data_processor.py (17 KB)
   └─ Veri yükleme (DB/CSV)
   └─ Veri temizleme
   └─ Veri birleştirme (4 tablo)

5. predictor.py (27 KB)
   └─ Random Forest model eğitimi
   └─ Tahmin yapma (1-12 ay)
   └─ Performans değerlendirme

6. visualizer.py (34 KB)
   └─ 6 grafik türü
   └─ İnteraktif plotlar
   └─ Renk şemaları
```

### Veri Akışı

```
Veri Kaynağı: PostgreSQL (4 Tablo)
    ↓
┌─────────────────────────────────────┐
│ bi_accruals (6,067 kayıt)           │ ← Fatura bilgileri
│ bi_accrual_terms (11,027 kayıt)     │ ← Dönem bilgileri
│ bi_accrual_fees (14,549 kayıt)      │ ← Ücret detayları
│ bi_accrual_fee_consumptions (33,352)│ ← Tüketim detayları
└─────────────────────────────────────┘
    ↓
Data Processor (data_processor.py)
    ├─ Veri yükleme (PostgreSQL)
    ├─ Tarih formatı dönüştürme
    ├─ Null değer filtreleme
    └─ Tablo birleştirme:
       1. Accruals + Terms → 11,027 (inner join)
       2. + Fees → 5,023 (inner join)
       3. + Consumptions → 12,959 (left join)
    ↓
İşlenmiş DataFrame (12,959 kayıt)
    ├─ total_consumption (kWh)
    ├─ term_total_cost (TL, KDV hariç)
    ├─ term_date (datetime)
    ├─ fee_code (tarife kategorisi)
    ├─ unit_price (TL/kWh)
    └─ consumption (kategori bazlı kWh)
    ↓
┌──────────────┬──────────────┐
│              │              │
Visualizer     Predictor
(Grafikler)    (ML Tahminleri)
    │              │
    │              ├─ Feature Engineering
    │              ├─ Random Forest Eğitimi
    │              ├─ Kategori Bazlı Maliyet
    │              └─ Tahmin (1-12 ay)
    │              │
    └──────────────┴──────────────
              ↓
    Streamlit Arayüzü (5 Sayfa)
    ├─ Ana Sayfa
    ├─ Tüketim Analizi
    ├─ Maliyet Analizi
    ├─ Tahminler
    └─ Detaylı Raporlar
```

---

## 🔧 Teknik Detaylar

### Yapılan İyileştirmeler

#### 1. **Veritabanı Entegrasyonu**

**PostgreSQL Bağlantısı:**
- SQLAlchemy engine ile connection pooling
- Pool size: 5, Max overflow: 10
- Pool timeout: 30s, Pool recycle: 1 saat
- Güvenli bağlantı bilgisi yönetimi (.env dosyası)

**Avantajlar:**
- Güncel veriye anlık erişim
- Daha hızlı veri yükleme (CSV'ye göre)
- Veri tutarlılığı (tek kaynak)
- Manuel CSV güncelleme gerektirmez

#### 2. **Performans Optimizasyonları**

**Cache Mekanizması:**
```python
@st.cache_data(ttl=3600)  # 1 saat cache
def load_data():
    # Veri yükleme işlemi
    pass

@st.cache_resource
def get_database_connection():
    # DB bağlantısı - tek instance
    pass
```
**Faydası:** İlk yüklemeden sonra 10x daha hızlı sayfa yüklenmeleri

**Efficient Data Merging:**
```python
# Inner join ile gereksiz veri filtreleme
df = accruals.merge(terms, on='id', how='inner')
# Left join ile eksik veriyi koruma
df = df.merge(consumptions, on='id', how='left')
```
**Faydası:** 33,352 kayıt → 12,959 kayda optimize edildi

#### 3. **Security Best Practices**

**Şifre Yönetimi:**
```python
# .env dosyası
DB_PASSWORD=your_password

# .gitignore
.env
```
**Faydası:** Hassas bilgiler kodda yok, Git'e yüklenmez

**URL Encoding:**
```python
from urllib.parse import quote_plus
password = quote_plus(os.getenv('DB_PASSWORD'))
```
**Faydası:** Özel karakterler güvenli hale gelir

**Singleton Pattern:**
```python
_db_manager = None
def get_database_manager():
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
```
**Faydası:** Tek bir DB instance, kaynak tasarrufu

#### 4. **Veri Kalitesi İyileştirmeleri**

**Outlier Temizliği:**
- IQR metoduyla outlier tespiti (5.0x katsayı - yumuşak)
- Sadece AŞIRI uç değerler temizlenir
- Normal mevsimsel dalgalanmalar korunur

**Duplikasyon Önleme:**
- `drop_duplicates(subset=['accrual_term_id'])` ile unique term garantisi
- Her term sadece bir kez hesaplarda kullanılır
- Doğru toplam hesaplaması

**Null Değer Filtreleme:**
- Boş ve null değerler otomatik filtrelenir
- Sıfır değerli kayıtlar grafiklerde gösterilmez
- Veri bütünlüğü sağlanır

#### 5. **Tarife Kategorisi Bazlı Maliyet Hesaplama**

**Kategori Dağılımı:**
- Her tarife kategorisi için ayrı birim fiyat
- Tüketim oranına göre ağırlıklı hesaplama
- Gerçek maliyetlere en yakın tahmin

**Örnek Hesaplama:**
```
4OG: %51.5 tüketim × 4.46 TL/kWh = 2.30 TL/kWh katkı
4AG: %27.0 tüketim × 2.14 TL/kWh = 0.58 TL/kWh katkı
URT: %15.0 tüketim × 3.20 TL/kWh = 0.48 TL/kWh katkı
Diğer: %6.5 tüketim × 5.00 TL/kWh = 0.33 TL/kWh katkı
─────────────────────────────────────────────────────
Toplam Ağırlıklı Birim Fiyat = 3.69 TL/kWh
```

---

### Proje Dosya Yapısı

```
enerji_analiz_projesi_v2/
├── app.py                      # Ana Streamlit uygulaması (26 KB)
├── config.py                   # Konfigürasyon ayarları (8 KB)
├── database.py                 # PostgreSQL bağlantı yöneticisi (8 KB)
├── data_processor.py           # Veri işleme modülü (17 KB)
├── predictor.py                # ML tahmin modülü (27 KB)
├── visualizer.py               # Grafik görselleştirme (34 KB)
├── requirements.txt            # Python bağımlılıkları
├── .env                        # Veritabanı bilgileri (GIT'e eklenmez)
├── .env.example                # Örnek .env dosyası
├── .gitignore                  # Git ignore dosyası
├── README.md                   # Bu dosya
└── KURULUM_REHBERI.md          # Detaylı kurulum rehberi
```

### Önemli Veri Sütunları

**Ana Sütunlar:**
- `accrual_term_id` - Birincil anahtar (unique kayıtlar)
- `total_consumption` - Hesaplanmış toplam tüketim (kWh)
- `term_total_cost` - KDV hariç toplam maliyet (TL)
- `term_date` - Fatura tarihi (datetime)
- `fee_code` - Tarife kategorisi (4AG_GUN, 4OG_GUN, vb.)
- `unit_price` - Kategori bazlı birim fiyat (TL/kWh)
- `consumption` - Kategori bazlı tüketim (kWh)

**Hesaplanmış Sütunlar:**
- `year`, `month`, `quarter` - Tarih özellikleri
- `season` - Mevsim (1-4)
- `is_summer`, `is_winter` - Binary feature'lar
- `months_from_start` - Time series feature

---

## 🐛 Sorun Giderme

### Veritabanı Bağlantı Hatası

**Çözüm 1: .env Dosyasını Kontrol Edin**
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=enerji_analiz_db
DB_USER=postgres
DB_PASSWORD=your_password
USE_DATABASE=True
```

**Çözüm 2: PostgreSQL Sunucusunun Çalıştığından Emin Olun**
```bash
# Windows
net start postgresql-x64-12

# Linux/Mac
sudo service postgresql start
```

**Çözüm 3: Veritabanı ve Tabloları Kontrol Edin**
```bash
python database.py
```

**Çözüm 4: Gerekli Kütüphaneleri Yükleyin**
```bash
pip install psycopg2-binary sqlalchemy python-dotenv
```

---

### Grafiklerde Veri Görünmüyor

**Çözüm: Cache'i Temizleyin**
- Streamlit uygulamasında `C` tuşuna basın
- Veya sağ üst köşeden "Clear Cache" seçin
- Veya sidebardan "🔄 Verileri Yenile" butonuna tıklayın

---

### Tarihler Yanlış Gösteriliyor

**Çözüm: Tarih Formatını Kontrol Edin**

Tarih formatı **YYYYMMDDHHmmss** olmalıdır:
```
Doğru: 20250226141640
Yanlış: 2025-02-26 14:16:40
```

---

### Yavaş Çalışıyor

**Açıklama:**
İlk yüklemede veri işleme ve model eğitimi nedeniyle yavaş olabilir.

**Çözüm:**
- Sonraki yüklemelerde cache sayesinde hızlanacaktır
- `@st.cache_data` ve `@st.cache_resource` dekoratörleri otomatik çalışır
- İlk yükleme: ~3 saniye
- Sonraki yüklemeler: <1 saniye

---

### Model Eğitim Hatası

**Hata Mesajı:** "Yetersiz veri - en az 10 kayıt gerekli"

**Çözüm:**
- Veritabanında yeterli veri olduğundan emin olun
- En az 10 aylık veri gereklidir
- Veriyi kontrol edin: Null değerler, outlier'lar

---

### CSV'ye Geri Dönmek İsterseniz

`.env` dosyasında:
```bash
USE_DATABASE=False
```

Veri dosyalarınızı `data/` klasörüne yerleştirin:
- `bi_accruals.csv`
- `bi_accrual_fees.csv`
- `bi_accrual_terms.csv`
- `bi_accrual_fee_consumptions.csv`

---

## 📞 İletişim

### Proje Bilgileri

- **Geliştirici:** Ece Erdem
- **Şirket:** Nar Sistem Enerji
- **Versiyon:** 2.0
- **Tarih:** 2025

### Sistem Gereksinimleri

- Python 3.8+
- 4 GB RAM (minimum)
- PostgreSQL 12+ (opsiyonel)
- Modern web tarayıcı (Chrome, Firefox, Edge)

### Kurulum Süresi

- Dependency kurulumu: ~5 dakika
- İlk konfigürasyon: ~10 dakika
- **Toplam:** ~15 dakika hazır

### Katkıda Bulunma

1. Bu repoyu fork edin
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

---

## 📄 Lisans

Bu proje Nar Sistem Enerji için geliştirilmiştir.

---

## 🎯 Özet

### Tek Cümlede

**"Enerji tüketim verilerini PostgreSQL veritabanından çekerek, Random Forest algoritması ile analiz eden, görselleştiren ve gelecek tüketimi tahmin eden Streamlit tabanlı web uygulaması."**

### Temel İstatistikler

- 📊 **12,959 işlem** analiz edildi
- ⚡ **106M+ kWh** tüketim veritabanında
- 💰 **₺72M+** maliyet takibi
- 🤖 **Random Forest** ML modeli (R²: 0.87)
- 📈 **6 grafik türü**
- 🔧 **15+ teknoloji entegrasyonu**
- ⏱️ **<1 saniye** sayfa yükleme (cache ile)
- 📱 **5 analiz sayfası**

### Başarı Kriterleri

✅ Tam fonksiyonel web uygulaması
✅ Yüksek doğruluk oranı (R²: 0.87)
✅ Kullanıcı dostu arayüz
✅ Kapsamlı dokümantasyon
✅ Production-ready kod kalitesi
✅ Security best practices
✅ Performance optimization
✅ Modüler ve genişletilebilir mimari

---

**"Veriyi anlayan, geleceği yönetir."**

---

**Enerji Analiz Sistemi v2.0**
© 2025 Nar Sistem Enerji
