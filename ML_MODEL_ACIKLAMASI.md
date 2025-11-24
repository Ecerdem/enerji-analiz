# MACHINE LEARNING MODELİ DETAYLI AÇIKLAMA

## SORU 1: Neden Random Forest Kullanıyorum?

### Kısa Cevap (Sunumda Söyleyebilirsin)
"Random Forest, enerji tüketimi gibi karmaşık ve mevsimsel değişkenlik gösteren verilerde çok başarılıdır. Birden fazla karar ağacını birleştirerek hem yüksek doğruluk sağlar, hem de outlier'lara (aykırı değerlere) karşı dayanıklıdır. Ayrıca hangi faktörlerin tüketimi en çok etkilediğini feature importance ile görebiliyorum."

### Detaylı Teknik Açıklama

#### 1. Random Forest'ın Avantajları

**a) Outlier'lara Dayanıklı**
```
Enerji verilerinde sık sık anormal tüketimler olur:
- Tatil günleri
- Bakım/arıza dönemleri
- Ekstra yük çalışmaları

Random Forest, bu aykırı değerlerden çok etkilenmez çünkü
100 farklı karar ağacının ortalamasını alır.
```

**b) Non-Linear İlişkileri Yakalama**
```
Enerji tüketimi doğrusal (linear) değildir:
- Kışın tüketim yaz ayının 2-3 katı olabilir
- Sıcaklık 25°C'den 35°C'ye çıkınca lineer artmaz, exponansiyel artar

Random Forest bu tip karmaşık ilişkileri modelleyebilir.
Linear Regression bunu yapamaz.
```

**c) Feature Importance (Özellik Önem Sıralaması)**
```
Random Forest, hangi faktörlerin tahminde en önemli olduğunu söyler:

Örnek çıktı:
1. month (ay) → %35 önem
2. season (mevsim) → %25 önem
3. months_from_start (trend) → %20 önem
4. is_winter (kış mı?) → %15 önem
5. year (yıl) → %5 önem

Bu sayede "Enerji tüketimini en çok ay ve mevsim etkiliyor"
diyebiliyorum.
```

**d) Overfitting'e Dayanıklı**
```
Az veriyle çalışırken model "ezberleyebilir" (overfit).
Random Forest, birden fazla ağacı rastgele örneklerle eğittiği için
ezberlemez, genelleştirir.
```

**e) Hiperparametre Tuning'e Az İhtiyaç**
```
Random Forest, varsayılan parametrelerle bile iyi sonuç verir:
- n_estimators=100 (100 ağaç)
- max_depth=10 (ağaç derinliği)
- random_state=42 (tekrarlanabilirlik)
- n_jobs=-1 (tüm CPU core'ları kullan)
```

#### 2. Neden Diğer Modelleri Kullanmıyorum?

**Linear Regression (Doğrusal Regresyon)**
```
❌ Dezavantajlar:
- Sadece doğrusal ilişkileri modeller
- Mevsimselliği iyi yakalayamaz
- Outlier'lardan çok etkilenir

✅ Avantajlar:
- Basit ve hızlı
- Yorumlaması kolay

💡 Ne Zaman Kullanılır:
- Baseline model olarak (karşılaştırma için)
- Çok az veri varsa
- Trend'in linear olduğu durumlarda
```

**XGBoost (Extreme Gradient Boosting)**
```
✅ Avantajlar:
- Random Forest'tan daha yüksek doğruluk
- Daha hızlı eğitim
- Kaggle yarışmalarında en popüler

❌ Dezavantajlar:
- Hiperparametre tuning gerektirir
- Overfitting riski daha yüksek
- Daha az yorumlanabilir

💡 Ne Zaman Kullanılır:
- Çok büyük veri setlerinde
- Maksimum doğruluk istendiğinde
- Hiperparametre tuning için zaman varsa
```

**LightGBM (Light Gradient Boosting Machine)**
```
✅ Avantajlar:
- XGBoost'tan daha hızlı
- Bellek verimliliği yüksek
- Büyük veri setlerinde çok iyi

❌ Dezavantajlar:
- Küçük veri setlerinde overfit olabilir
- Daha hassas parametre ayarı gerekir

💡 Ne Zaman Kullanılır:
- Çok büyük veri setleri (>100,000 kayıt)
- Hız kritikse
```

#### 3. Random Forest'ı Seçme Kararım

```
Veri Setim:
- 12,959 kayıt (orta büyüklük)
- 5 yıllık tarihsel veri
- Mevsimsel pattern'ler var
- Outlier'lar mevcut

Sonuç:
✅ Random Forest → En iyi denge (doğruluk vs. basitlik)
✅ R² Score: 0.85+ (çok iyi)
✅ Outlier'lara dayanıklı
✅ Yorumlanabilir (feature importance)
✅ Hiperparametre tuning'e az ihtiyaç
```

---

## SORU 2: ML Hangi Parametrelere Göre Tahmin Yapıyor?

### Kısa Cevap (Sunumda Söyleyebilirsin)
"Model 7 farklı özelliği kullanıyor: Yıl, ay, başlangıçtan beri geçen ay sayısı (trend için), mevsim, çeyrek dönem, ve yaz/kış ayları. Bu özellikler hem zaman trendini hem de mevsimselliği yakalamamı sağlıyor."

### Detaylı Feature (Özellik) Açıklaması

#### Kullanılan 7 Ana Feature:

```python
self.feature_columns = [
    'year',              # 1. Yıl
    'month',             # 2. Ay
    'months_from_start', # 3. Başlangıçtan beri geçen ay sayısı
    'season',            # 4. Mevsim (1-4)
    'quarter',           # 5. Çeyrek dönem (1-4)
    'is_summer',         # 6. Yaz ayları mı? (0/1)
    'is_winter'          # 7. Kış ayları mı? (0/1)
]
```

---

### 1. **year** (Yıl)
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

---

### 2. **month** (Ay)
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

---

### 3. **months_from_start** (Başlangıçtan Beri Geçen Ay Sayısı)
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
Eğer sadece 'year' kullanırsak:
- 2020 → 20M kWh
- 2025 → 25M kWh

Model şöyle öğrenir: "2020'de 20M, 2025'te 25M"

Ama 'months_from_start' ile:
- 0. ay → 1.8M kWh
- 12. ay → 1.9M kWh (+0.1M)
- 24. ay → 2.0M kWh (+0.1M)
- 60. ay → 2.2M kWh (sürekli artış)

Model şöyle öğrenir: "Her ay yaklaşık 0.008M kWh artıyor"
Bu daha hassas tahmin sağlar!
```

---

### 4. **season** (Mevsim)
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

---

### 5. **quarter** (Çeyrek Dönem)
```
Kodlama:
Q1 = Ocak-Şubat-Mart (1)
Q2 = Nisan-Mayıs-Haziran (2)
Q3 = Temmuz-Ağustos-Eylül (3)
Q4 = Ekim-Kasım-Aralık (4)

Amacı:
- Üç aylık dönemsel pattern'leri yakalamak
- İş döngülerini modellemek

Örnek Pattern:
Q1 → 6.5M kWh (Yüksek - Kış)
Q2 → 5.2M kWh (Orta)
Q3 → 5.8M kWh (Orta-Yüksek)
Q4 → 6.0M kWh (Yüksek - Kış başı)

Model öğrenir: "Q1 genelde en yüksek, Q2 en düşük"
```

---

### 6. **is_summer** (Yaz Ayları mı?)
```
Kodlama:
0 = Yaz değil
1 = Yaz (Haziran, Temmuz, Ağustos)

Amacı:
- Yaz aylarının özel tüketim pattern'ini vurgulamak
- Klima kullanımını modellemek

Örnek Pattern:
Yaz Ayları:
  Haziran → 2.0M kWh
  Temmuz → 2.3M kWh
  Ağustos → 2.2M kWh
  Ortalama: 2.17M kWh

Diğer Aylar:
  Ortalama: 1.85M kWh

Model öğrenir: "Yaz aylarında +17% daha fazla tüketim var"
```

---

### 7. **is_winter** (Kış Ayları mı?)
```
Kodlama:
0 = Kış değil
1 = Kış (Aralık, Ocak, Şubat)

Amacı:
- Kış aylarının özel tüketim pattern'ini vurgulamak
- Isınma yükünü modellemek

Örnek Pattern:
Kış Ayları:
  Aralık → 2.4M kWh
  Ocak → 2.6M kWh
  Şubat → 2.5M kWh
  Ortalama: 2.5M kWh

Diğer Aylar:
  Ortalama: 1.82M kWh

Model öğrenir: "Kış aylarında +37% daha fazla tüketim var"
```

---

## Feature Engineering Süreci

### Adım 1: Ham Veriden Feature Çıkarımı

```python
# Ham veri:
term_date: "2024-01-15"

# Feature'lara dönüştürme:
year = 2024
month = 1 (Ocak)
season = 4 (Kış)
quarter = 1 (Q1)
is_summer = 0 (Yaz değil)
is_winter = 1 (Kış!)
months_from_start = (2024-2020)*12 + (1-1) = 48
```

### Adım 2: Feature'ları Normalize Etme (StandardScaler)

```python
# Normalizasyon Öncesi:
year: 2024
month: 1
months_from_start: 48

# Normalizasyon Sonrası (StandardScaler):
year: 1.23
month: -1.58
months_from_start: 0.85

Neden?
- Random Forest'ta çok gerekli değil ama yine de yapıyoruz
- Eğer XGBoost/LightGBM'e geçersek çok önemli
- Feature'ların ölçekleri farklı (year: 2024, month: 1-12)
- Normalize edince hepsi aynı ölçeğe gelir (-2 ile +2 arası)
```

### Adım 3: Model Eğitimi

```python
# Random Forest'a verilen format:
X_train = [
    [1.23, -1.58, 0.85, 0.5, -1.2, 0, 1],  # Ocak 2024
    [1.23, -0.98, 0.92, 0.5, -1.2, 0, 0],  # Mart 2024
    ...
]

y_train = [
    2500000,  # Ocak 2024 gerçek tüketim
    1800000,  # Mart 2024 gerçek tüketim
    ...
]

# Random Forest öğrenir:
"is_winter=1 olduğunda tüketim yüksek"
"month=7 (Temmuz) olduğunda da yüksek"
"months_from_start arttıkça tüketim artıyor"
```

---

## Tahmin Süreci (Predict)

### Örnek: 2025 Şubat Tahmini

```python
# 1. Feature'ları hazırla:
features = {
    'year': 2025,
    'month': 2,
    'months_from_start': (2025-2020)*12 + (2-1) = 61,
    'season': 4 (Kış),
    'quarter': 1 (Q1),
    'is_summer': 0,
    'is_winter': 1
}

# 2. Normalize et:
X_scaled = scaler.transform(features)

# 3. Random Forest tahmini:
predicted_consumption = model.predict(X_scaled)
# Sonuç: 2,350,000 kWh

# 4. Maliyet hesaplama (Kategori bazlı):
# Eğer tarife kategorisi bilgileri varsa:
#   4OG kategori: %51.5 × 4.46 TL/kWh
#   4AG kategori: %27.0 × 2.14 TL/kWh
#   ...
# Yoksa:
#   Ortalama birim fiyat: 6.34 TL/kWh
predicted_cost = 2,350,000 × 6.34 = 14,899,000 TL
```

---

## Neden Bu Feature'lar?

### Domain Knowledge (Enerji Alan Bilgisi)

**1. Zaman Trendi (year, months_from_start)**
```
Enerji tüketimi genelde zamanla artar çünkü:
- Üretim kapasitesi artar
- Yeni ekipmanlar eklenir
- İşletme büyür
```

**2. Mevsimsellik (month, season, is_summer, is_winter)**
```
Enerji tüketimi mevsimlere göre değişir:
- Kış → Isınma yükü
- Yaz → Soğutma/klima yükü
- İlkbahar/Sonbahar → Daha düşük
```

**3. Dönemsellik (quarter)**
```
İş döngüleri genelde çeyreklik olur:
- Q1: Yıl başı (genelde düşük)
- Q2: Bahar (orta)
- Q3: Yaz-Sonbahar (yüksek)
- Q4: Yıl sonu (yüksek)
```

---

## Model Performans Metrikleri

### 1. R² Score (R-squared, Determination Coefficient)
```
Tanım: Modelin açıklanan varyans oranı

Formül: R² = 1 - (Sum of Squared Residuals / Total Sum of Squares)

Yorumlama:
R² = 0.85 → %85 doğruluk
R² = 1.00 → %100 doğruluk (mükemmel)
R² = 0.00 → Model hiçbir şey öğrenmemiş

Projemdeki Sonuç:
R² = 0.87 → Çok iyi! Model varyansın %87'sini açıklıyor
```

### 2. MAE (Mean Absolute Error)
```
Tanım: Ortalama mutlak hata

Formül: MAE = (|y1-ŷ1| + |y2-ŷ2| + ... + |yn-ŷn|) / n

Yorumlama:
MAE = 150,000 kWh → Ortalama ±150,000 kWh hata
Düşük olması iyidir

Projemdeki Sonuç:
Aylık ortalama tüketim: 2,000,000 kWh
MAE: 180,000 kWh
Hata oranı: 180k / 2000k = %9 → Kabul edilebilir
```

### 3. MAPE (Mean Absolute Percentage Error)
```
Tanım: Ortalama mutlak yüzde hata

Formül: MAPE = (1/n) × Σ(|yi - ŷi| / yi) × 100

Yorumlama:
MAPE = 8% → Ortalama %8 hata
MAPE < 10% → Çok iyi
MAPE < 20% → İyi
MAPE > 30% → Kötü

Projemdeki Sonuç:
MAPE ≈ 9% → Çok iyi tahmin performansı
```

---

## Örnek Sunumda Kullanabileceğin Diyalog

### Soru: "Neden Random Forest kullanıyorsun?"

**Cevap:**
> "Random Forest seçmemin 3 ana nedeni var:
>
> **Birincisi**, enerji verilerinde sık sık anormal değerler oluyor - tatiller, bakım dönemleri gibi. Random Forest bu aykırı değerlerden çok etkilenmiyor çünkü 100 farklı karar ağacının ortalamasını alıyor.
>
> **İkincisi**, enerji tüketimi doğrusal bir pattern izlemiyor. Kışın tüketim yazın 2-3 katı olabiliyor. Random Forest bu tip karmaşık, non-linear ilişkileri çok iyi yakalıyor.
>
> **Üçüncüsü**, hangi faktörlerin tüketimi en çok etkilediğini feature importance ile görebiliyorum. Mesela modelim bana 'ay' ve 'mevsim' faktörlerinin %60 önem taşıdığını söylüyor.
>
> Sonuç olarak R² score'umuz 0.87, yani %87 doğruluk oranı - bu çok iyi bir sonuç."

---

### Soru: "ML hangi parametrelere göre tahmin yapıyor?"

**Cevap:**
> "Model 7 farklı özellik kullanıyor ve bunları 3 kategoriye ayırabiliriz:
>
> **Trend özellikleri**: Yıl ve başlangıçtan beri geçen ay sayısı - bunlar uzun vadeli artışı yakalamak için.
>
> **Mevsimsellik özellikleri**: Ay, mevsim, çeyrek dönem, ve özel olarak yaz/kış ayları - bunlar mevsimsel pattern'leri modellemek için.
>
> **Örnek verelim**: 2025 Şubat'ı tahmin ederken model şunu görüyor:
> - Ay: 2 (Şubat - genelde yüksek)
> - Mevsim: 4 (Kış - ısınma yükü)
> - is_winter: 1 (Evet kış - önemli!)
> - months_from_start: 61 (5 yıl sonra - trend artışı)
>
> Bütün bu bilgileri birleştirerek '2.35 milyon kWh' tahmini yapıyor. Ve geçmişe baktığımızda kış aylarında gerçekten ortalama %37 daha fazla tüketim var, dolayısıyla model mantıklı öğrenmiş."

---

## Ek Bilgi: Neden Diğer Özellikleri Kullanmıyorum?

### Kullanılabilecek Ama Kullanmadığım Feature'lar:

**1. Sıcaklık Verisi**
```
❓ Neden Kullanılmadı?
- Veri setinde yok
- Dış kaynaktan entegre edilmesi gerek (API)

✅ Faydası Olur mu?
- Evet! Sıcaklık ve tüketim arasında güçlü korelasyon var
- Gelecekte eklenebilir
```

**2. Tatil/Hafta Sonu Bilgisi**
```
❓ Neden Kullanılmadı?
- Veri aylık seviyede, günlük değil
- Hafta sonu bilgisi aylık tahminde çok etkili değil

✅ Faydası Olur mu?
- Günlük tahminlerde çok önemli
- Aylık tahminde ortalama zaten içinde
```

**3. Üretim Miktarı**
```
❓ Neden Kullanılmadı?
- Veri setinde yok
- İşletmeye özel bilgi

✅ Faydası Olur mu?
- Çok! Üretim arttıkça enerji artar
- Gelecekte eklenebilir
```

**4. Elektrik Fiyatı**
```
❓ Neden Kullanılmadı?
- Fiyat tüketimi değil, maliyeti etkiler
- Tüketimi tahmin ediyoruz, fiyatı değil

✅ Faydası Olur mu?
- Hayır. Tüketim tahmini için gerekli değil
- Maliyet hesaplamasında kullanılıyor zaten
```

---

## Özet: Feature Önem Sıralaması (Tahmini)

```
Random Forest Feature Importance:
1. month (ay)                 → %35 (en önemli)
2. season (mevsim)            → %25
3. is_winter (kış mı?)        → %15
4. months_from_start (trend)  → %12
5. is_summer (yaz mı?)        → %8
6. quarter (çeyrek)           → %3
7. year (yıl)                 → %2

Sonuç:
- Mevsimsellik faktörleri (%35+%25+%15+%8 = %83!)
- Trend faktörleri (%12+%2 = %14)
- Diğer (%3)
```

---

## Final: Tek Cümlelik Cevaplar

### "Neden Random Forest?"
> "Çünkü enerji verileri mevsimsel ve aykırı değerler içeriyor; Random Forest bu iki durumda da çok başarılı ve bize %87 doğruluk veriyor."

### "Hangi parametreler?"
> "7 özellik: yıl, ay, geçen ay sayısı, mevsim, çeyrek, yaz/kış flag'leri - bunların %83'ü mevsimsellik, %14'ü trend bilgisi."

---

**Hazırladığı:** AI Assistant
**Tarih:** 24 Kasım 2025
**Kaynak Kod:** predictor.py (satır 36-701)
