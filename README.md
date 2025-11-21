# Enerji Tüketim Analiz ve Tahmin Sistemi

Modern ve kullanıcı dostu bir enerji tüketim analiz platformu. Streamlit tabanlı web arayüzü ile enerji tüketim verilerinizi analiz edin, görselleştirin ve gelecek tahminleri yapın.

## 📋 Proje Özeti

**Veri İstatistikleri:**
- **Toplam Kayıt:** 12,959 işlem
- **Toplam Tüketim:** 106+ Milyon kWh
- **Toplam Maliyet:** ₺72+ Milyon
- **Tarih Aralığı:** 2020 - 2025
- **Unique Fatura:** 2,711 adet

## Özellikler

### Ana Sayfalar

**Ana Sayfa**
- Genel özet metrikleri (toplam tüketim, maliyet)
- En yüksek/düşük tüketim ayları
- Hızlı bakış grafikleri

**Tüketim Analizi**
- Aylık tüketim trend grafiği
- Mevsimsel analiz
- Isı haritası görselleştirmesi

**Maliyet Analizi**
- Aylık maliyet trendi (Net + KDV)
- Yıllık karşılaştırma
- Birim fiyat hesaplamaları
- Yıllık artış oranları

**Tahminler**
- Machine Learning ile gelecek tahminleri
- 1-12 ay arası tahmin seçenekleri
- Model performans metrikleri
- CSV export desteği

**Detaylı Raporlar**
- Aylık detay raporu
- Yıllık özet raporu
- Ham veri görüntüleme ve filtreleme
- CSV indirme

## Kurulum

### Gereksinimler

- Python 3.8 veya üzeri
- pip paket yöneticisi
- PostgreSQL 12+ (veritabanı kullanımı için)

### Adımlar

1. Gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

2. **Veri Kaynağı Seçimi:**

   Sistem iki farklı veri kaynağını destekler:

   #### A) PostgreSQL Veritabanı (Önerilen)

   **Avantajlar:**
   - Güncel veriye anlık erişim
   - Daha hızlı veri yükleme
   - Veri tutarlılığı (tek kaynak)
   - Manuel CSV güncelleme gerektirmez

   **Kurulum:**

   a) `.env` dosyasını düzenleyin (`.env.example` dosyasından kopyalayabilirsiniz):
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

   b) PostgreSQL'de gerekli tabloları oluşturun:
   - `bi_accruals`
   - `bi_accrual_fees`
   - `bi_accrual_terms`
   - `bi_accrual_fee_consumptions`

   c) Veritabanı bağlantısını test edin:
   ```bash
   python database.py
   ```

   #### B) CSV Dosyaları (Geriye Dönük Uyumluluk)

   `.env` dosyasında:
   ```bash
   USE_DATABASE=False
   ```

   Veri dosyalarınızı `data/` klasörüne yerleştirin:
   - bi_accruals.csv (6,067 kayıt)
   - bi_accrual_fees.csv (14,549 kayıt)
   - bi_accrual_terms.csv (11,027 kayıt)
   - bi_accrual_fee_consumptions.csv (33,352 kayıt)

3. Uygulamayı çalıştırın:
```bash
streamlit run app.py
```

4. Tarayıcınızda açın:
```
http://localhost:8501
```

## Proje Yapısı

```
enerji_analiz_projesi/
├── app.py                  # Ana uygulama dosyası
├── config.py              # Yapılandırma ayarları
├── database.py            # Veritabanı bağlantı yöneticisi
├── data_processor.py      # Veri işleme modülü (DB/CSV desteği)
├── predictor.py           # ML tahmin modülü
├── visualizer.py          # Grafik görselleştirme modülü
├── requirements.txt       # Python bağımlılıkları
├── .env                   # Veritabanı bağlantı bilgileri (GIT'e eklenmez)
├── .env.example           # Örnek .env dosyası
├── data/                  # Veri dosyaları klasörü (CSV kullanımı için)
│   ├── bi_accruals.csv           (6,067 kayıt)
│   ├── bi_accrual_fees.csv       (14,549 kayıt)
│   ├── bi_accrual_terms.csv      (11,027 kayıt)
│   └── bi_accrual_fee_consumptions.csv (33,352 kayıt)
├── .gitignore            # Git ignore dosyası
└── README.md             # Bu dosya
```

## Teknik Detaylar

### Yapılan İyileştirmeler

**Veritabanı Entegrasyonu (YENİ!)**
- PostgreSQL bağlantı desteği (SQLAlchemy)
- CSV geriye dönük uyumluluğu korundu
- Otomatik veri kaynağı seçimi (.env ile)
- Connection pooling ile performans optimizasyonu
- Güvenli bağlantı bilgisi yönetimi (.env dosyası)

**Veri İşleme (data_processor.py)**
- Hem veritabanı hem CSV desteği
- Tarih formatı düzeltildi: YYYYMMDDHHmmss formatından datetime'a dönüştürme
- Birleştirme optimizasyonu: Inner join ile gereksiz kayıtlar elendi
- Tüketim hesaplaması: `accrual_term_id` bazında doğru toplam hesaplama
- Debug bilgileri: İşlem sırasında detaylı bilgi gösterimi

**Görselleştirme (visualizer.py)**
- Duplikasyon önleme: `drop_duplicates()` ile tekrarlı kayıtlar temizlendi
- Boş veri filtreleme: Sıfır değerli kayıtlar grafiklerde gösterilmiyor
- Trend hesaplaması: En az 2 nokta kontrolü ile hata önleme
- Özet metrikler: Unique term bazında doğru hesaplama

**Uygulama Akışı (app.py)**
- Yıllık raporlar: Unique term bazında hesaplama
- Birim fiyat: Sıfıra bölme hatası önleme
- Filtreleme: Boş ve sıfır değerli satırlar otomatik filtreleniyor

### Veri Akışı

```
1. Accruals + Terms  → 11,027 kayıt (inner join)
2. + Fees           → 5,023 kayıt (inner join)
3. + Consumptions   → 12,959 kayıt (left join)
4. Hesaplamalar     → Total, KDV, Grand Total
```

### Önemli Veri Sütunları

- **`accrual_term_id`**: Birincil anahtar (unique kayıtlar için)
- **`total_consumption`**: Hesaplanmış toplam tüketim (kWh)
- **`grand_total`**: KDV dahil toplam maliyet (TL)
- **`term_date`**: Fatura tarihi

### Veri İşleme
- Tarih formatı: YYYYMMDDHHmmss
- Inner join ile gereksiz kayıtlar elendi
- Unique `accrual_term_id` bazında hesaplamalar
- Sıfır ve boş değerler otomatik filtrelenir

### Görselleştirme
- Plotly ile interaktif grafikler
- Duplikasyon önleme mekanizması
- Responsive tasarım
- Özelleştirilebilir renk şemaları

### Tahmin Modeli
- Scikit-learn tabanlı ML modeli
- Model performans metrikleri (R² Score, MAE)
- Cache mekanizması ile hızlı yükleme
- 1-12 ay arası tahmin desteği

## Kullanım

### Veri Yükleme
Uygulama otomatik olarak `data/` klasöründeki CSV dosyalarını yükler ve işler.

### Grafik Etkileşimi
- Zoom: Fare ile sürükle
- Pan: Shift + sürükle
- Reset: Çift tıklama
- Export: Grafik üzerindeki kamera ikonu

### Raporlar
Tüm raporlar CSV formatında indirilebilir ve filtrelenebilir.

## Sorun Giderme

### Veritabanı bağlantı hatası
1. `.env` dosyasındaki bağlantı bilgilerini kontrol edin
2. PostgreSQL sunucusunun çalıştığından emin olun
3. Veritabanı ve tabloların var olduğunu doğrulayın:
   ```bash
   python database.py
   ```
4. Gerekli kütüphanelerin yüklü olduğunu kontrol edin:
   ```bash
   pip install psycopg2-binary sqlalchemy python-dotenv
   ```

### CSV'ye geri dönmek isterseniz
`.env` dosyasında:
```bash
USE_DATABASE=False
```

### Grafiklerde veri görünmüyor
Cache'i temizleyin:
- Streamlit uygulamasında `C` tuşuna basın
- Veya sağ üst köşeden "Clear Cache" seçin

### Tarihler yanlış gösteriliyor
Tarih formatı YYYYMMDDHHmmss olmalıdır (örn: 20250226141640)

### Yavaş çalışıyor
İlk yüklemede veri işleme ve model eğitimi nedeniyle yavaş olabilir. Sonraki yüklemelerde cache sayesinde hızlanacaktır. `@st.cache_data` ve `@st.cache_resource` dekoratörleri kullanılmaktadır.

### Veri yükleme hatası
- **Veritabanı kullanıyorsanız:** Bağlantı bilgilerini ve tablo varlığını kontrol edin
- **CSV kullanıyorsanız:** `data/` klasöründe gerekli CSV dosyalarının olduğundan emin olun

## Önemli Notlar

- Tüm hesaplamalar **unique `accrual_term_id`** bazında yapılmaktadır
- KDV oranı %20 olarak sabit kabul edilmiştir
- Sıfır ve boş değerler otomatik filtrelenmektedir
- CSV dosyaları UTF-8 encoding ile kaydedilmelidir

## Katkıda Bulunma

1. Bu repoyu fork edin
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

## Lisans

Bu proje Nar Sistem Enerji için geliştirilmiştir.

## İletişim

Sorularınız için lütfen iletişime geçin.

---

**Enerji Analiz Sistemi v1.0**
Geliştirici: Nar Sistem Enerji
