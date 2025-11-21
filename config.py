"""
Enerji Analiz Sistemi - Konfigürasyon Ayarları
Tüm sabit değerler ve ayarlar bu dosyada merkezi olarak yönetilir.
"""

import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()


class Config:
    """Ana konfigürasyon sınıfı."""

    # Proje kök dizini
    BASE_DIR: Path = Path(__file__).parent.resolve()

    # Veri kaynağı ayarları
    USE_DATABASE: bool = os.getenv('USE_DATABASE', 'True').lower() == 'true'

    # Veritabanı ayarları (PostgreSQL)
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: str = os.getenv('DB_PORT', '5432')
    DB_NAME: str = os.getenv('DB_NAME', 'enerji_analiz_db')
    DB_USER: str = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', '')
    DB_SCHEMA: str = os.getenv('DB_SCHEMA', 'public')

    # Veritabanı tablo isimleri
    DB_TABLE_ACCRUALS: str = "bi_accruals"
    DB_TABLE_ACCRUAL_FEES: str = "bi_accrual_fees"
    DB_TABLE_ACCRUAL_TERMS: str = "bi_accrual_terms"
    DB_TABLE_ACCRUAL_FEE_CONSUMPTIONS: str = "bi_accrual_fee_consumptions"

    @classmethod
    def get_full_table_name(cls, table_name: str) -> str:
        """Schema ile birlikte tam tablo adını döndürür."""
        return f"{cls.DB_SCHEMA}.{table_name}"

    REQUIRED_DB_TABLES: List[str] = [
        DB_TABLE_ACCRUALS,
        DB_TABLE_ACCRUAL_FEES,
        DB_TABLE_ACCRUAL_TERMS,
        DB_TABLE_ACCRUAL_FEE_CONSUMPTIONS
    ]

    # Veri klasörü ayarları (CSV için - geriye dönük uyumluluk)
    DATA_FOLDER: str = "data"
    DATA_FOLDER_PATH: Path = BASE_DIR / DATA_FOLDER

    # Gerekli CSV dosyaları
    REQUIRED_CSV_FILES: List[str] = [
        "bi_accruals.csv",
        "bi_accrual_fees.csv",
        "bi_accrual_terms.csv",
        "bi_accrual_fee_consumptions.csv"
    ]

    # İş mantığı sabitleri
    VAT_RATE: float = 0.20  # KDV oranı (%20)
    CURRENCY: str = "TL"
    CURRENCY_SYMBOL: str = "₺"

    # Machine Learning ayarları
    ML_TEST_SPLIT_RATIO: float = 0.2
    ML_MIN_TRAINING_SAMPLES: int = 10
    ML_RANDOM_STATE: int = 42
    ML_MAX_PREDICTION_MONTHS: int = 12
    ML_MIN_PREDICTION_MONTHS: int = 1
    ML_DEFAULT_PREDICTION_MONTHS: int = 6

    # Performans ayarları
    EPSILON: float = 1e-6  # Sıfıra bölme kontrolü için minimum değer

    # Streamlit ayarları
    ST_PAGE_TITLE: str = "Enerji Analiz Sistemi"
    ST_PAGE_ICON: str = "⚡"
    ST_LAYOUT: str = "wide"
    ST_SIDEBAR_STATE: str = "expanded"

    # Logging ayarları
    LOG_FILE: str = "app.log"
    LOG_MAX_BYTES: int = 10_000_000  # 10MB
    LOG_BACKUP_COUNT: int = 5
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Grafik renk paleti
    COLOR_SCHEME: dict = {
        'primary': '#1f77b4',
        'secondary': '#ff7f0e',
        'success': '#2ca02c',
        'danger': '#d62728',
        'warning': '#ff9800',
        'info': '#17a2b8'
    }

    # Mevsim tanımları
    SEASONS: dict = {
        1: "Kış",      # Aralık, Ocak, Şubat
        2: "İlkbahar",  # Mart, Nisan, Mayıs
        3: "Yaz",       # Haziran, Temmuz, Ağustos
        4: "Sonbahar"   # Eylül, Ekim, Kasım
    }

    SEASON_COLORS: dict = {
        'Kış': '#3498db',
        'İlkbahar': '#2ecc71',
        'Yaz': '#f39c12',
        'Sonbahar': '#e74c3c'
    }

    # Ay isimleri (Türkçe)
    MONTH_NAMES_TR: List[str] = [
        'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
        'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'
    ]

    MONTH_NAMES_SHORT_TR: List[str] = [
        'Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz',
        'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara'
    ]

    # Tarih formatları
    DATE_FORMAT_INPUT: str = '%Y%m%d%H%M%S'
    DATE_FORMAT_DISPLAY: str = '%Y-%m-%d'
    DATE_FORMAT_MONTH_YEAR: str = '%Y-%m'

    @classmethod
    def validate_data_folder(cls) -> bool:
        """
        Veri klasörünün varlığını ve gerekli dosyaları kontrol et.

        Returns:
            bool: Tüm dosyalar mevcutsa True
        """
        if not cls.DATA_FOLDER_PATH.exists():
            return False

        for filename in cls.REQUIRED_CSV_FILES:
            file_path = cls.DATA_FOLDER_PATH / filename
            if not file_path.exists():
                return False

        return True

    @classmethod
    def get_missing_files(cls) -> List[str]:
        """
        Eksik CSV dosyalarının listesini döndür.

        Returns:
            List[str]: Eksik dosya isimleri
        """
        missing = []

        if not cls.DATA_FOLDER_PATH.exists():
            return cls.REQUIRED_CSV_FILES

        for filename in cls.REQUIRED_CSV_FILES:
            file_path = cls.DATA_FOLDER_PATH / filename
            if not file_path.exists():
                missing.append(filename)

        return missing

    @classmethod
    def validate_database(cls) -> bool:
        """
        Veritabanı bağlantısını ve gerekli tabloları kontrol et.

        Returns:
            bool: Bağlantı başarılı ve tüm tablolar mevcutsa True
        """
        try:
            from database import get_database_manager

            db_manager = get_database_manager()

            # Bağlantıyı test et
            if not db_manager.test_connection():
                return False

            # Gerekli tabloları kontrol et
            for table_name in cls.REQUIRED_DB_TABLES:
                if not db_manager.check_table_exists(table_name):
                    return False

            return True

        except Exception as e:
            print(f"Veritabanı validasyon hatası: {str(e)}")
            return False

    @classmethod
    def get_missing_tables(cls) -> List[str]:
        """
        Eksik veritabanı tablolarının listesini döndür.

        Returns:
            List[str]: Eksik tablo isimleri
        """
        try:
            from database import get_database_manager

            db_manager = get_database_manager()

            # Bağlantıyı test et
            if not db_manager.test_connection():
                return cls.REQUIRED_DB_TABLES

            missing = []
            for table_name in cls.REQUIRED_DB_TABLES:
                if not db_manager.check_table_exists(table_name):
                    missing.append(table_name)

            return missing

        except Exception:
            return cls.REQUIRED_DB_TABLES


class DevelopmentConfig(Config):
    """Geliştirme ortamı konfigürasyonu."""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"


class ProductionConfig(Config):
    """Production ortamı konfigürasyonu."""
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"


class TestConfig(Config):
    
    """Test ortamı konfigürasyonu."""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    DATA_FOLDER: str = "test_data"
    ML_MIN_TRAINING_SAMPLES: int = 5


# Aktif konfigürasyon (environment'a göre)
def get_config() -> Config:
    """
    Çevre değişkenine göre uygun config döndür.

    Returns:
        Config: Aktif konfigürasyon
    """
    env = os.getenv("ENV", "development").lower()

    if env == "production":
        return ProductionConfig()
    elif env == "test":
        return TestConfig()
    else:
        return DevelopmentConfig()
