# Kurulum Rehberi - Yeni Başlayanlar İçin

Bu rehber, projeyi ilk kez çalıştıracaklar için adım adım kurulum talimatlarını içerir.

## 1. Virtual Environment Aktifleştirme

Virtual environment zaten oluşturuldu. Şimdi aktifleştirin:

```bash
# Windows için:
venv\Scripts\activate

# Aktifleştiğinde komut satırınızda (venv) yazısını göreceksiniz
```

## 2. Gerekli Kütüphaneleri Yükleme

```bash
pip install -r requirements.txt
```

Bu komut aşağıdaki kütüphaneleri yükleyecek:
- Streamlit (Web arayüzü)
- Pandas (Veri işleme)
- Plotly (Grafikler)
- Scikit-learn (ML modeli)
- PostgreSQL bağlantı araçları

## 3. Veritabanı Ayarları

`.env.example` dosyasını `.env` olarak kopyalayın ve düzenleyin:

```bash
# Windows için:
copy .env.example .env

# Sonra .env dosyasını bir metin editörü ile açın ve düzenleyin
```

### Seçenek A: PostgreSQL Kullanımı (Önerilen)
```
USE_DATABASE=True
DB_HOST=localhost
DB_PORT=5432
DB_NAME=enerji_analiz_db
DB_USER=postgres
DB_PASSWORD=sizin_sifreniz
```

### Seçenek B: CSV Kullanımı (Daha Basit)
```
USE_DATABASE=False
```

CSV kullanacaksanız, veri dosyalarını `data/` klasörüne koyun.

## 4. Uygulamayı Başlatma

```bash
streamlit run app.py
```

Tarayıcınızda otomatik olarak açılacak: http://localhost:8501

## 5. Git Kullanımı (Günlük Çalışma)

### Her çalışma başında:
```bash
git status  # Durumu kontrol et
```

### Kod yazdıktan sonra:
```bash
git add .
git commit -m "Ne değiştirdiniz (örn: 'Grafik renklerini güncelledim')"
```

### Commit geçmişini görmek için:
```bash
git log --oneline
```

### Hata yaptıysanız geri almak için:
```bash
git restore dosya_adi.py  # Tek dosyayı geri al
git restore .              # Tüm değişiklikleri geri al
```

## 6. Virtual Environment Kapatma

İşiniz bittiğinde:
```bash
deactivate
```

## Sık Karşılaşılan Sorunlar

### Sorun: "streamlit komut bulunamadı"
**Çözüm:** Virtual environment'ı aktifleştirmeyi unuttunuz:
```bash
venv\Scripts\activate
```

### Sorun: "ModuleNotFoundError"
**Çözüm:** Kütüphaneler yüklenmemiş:
```bash
pip install -r requirements.txt
```

### Sorun: ".env dosyası bulunamadı"
**Çözüm:** `.env.example` dosyasını kopyalayıp `.env` olarak kaydedin

### Sorun: "Database bağlantı hatası"
**Çözüm:** `.env` dosyasında `USE_DATABASE=False` yapın (CSV kullanmak için)

## Günlük Çalışma Rutini

```bash
# 1. Terminal açın ve proje klasörüne gidin
cd C:\Users\Monster\Desktop\enerji_analiz_projesi_BACKUP_2025_11_17

# 2. Virtual environment aktif edin
venv\Scripts\activate

# 3. Uygulamayı çalıştırın
streamlit run app.py

# 4. Kod geliştirin...

# 5. Değişiklikleri kaydedin
git add .
git commit -m "Bugün ne yaptınız"

# 6. İşiniz bitince
deactivate
```

## Yardım Alma

- Git komutları: `git help`
- Streamlit dokümantasyonu: https://docs.streamlit.io
- Python dokümantasyonu: https://docs.python.org/3/

## Önemli Notlar

- ✅ Her anlamlı değişiklikten sonra commit yapın
- ✅ Virtual environment'ı her zaman aktif tutun
- ✅ `.env` dosyasını asla Git'e eklemeyin
- ✅ Hata aldığınızda `git status` ile durumu kontrol edin
- ✅ Büyük değişiklikler öncesi yeni branch oluşturun

İyi çalışmalar!
