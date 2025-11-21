"""
Veritabanı bağlantı yönetimi modülü.
PostgreSQL veritabanına SQLAlchemy ile bağlantı sağlar.
"""

import os
from typing import Optional
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import logging

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    PostgreSQL veritabanı bağlantı yöneticisi.

    .env dosyasından bağlantı bilgilerini okur ve
    SQLAlchemy engine oluşturur.
    """

    def __init__(self):
        """DatabaseManager başlatıcı."""
        self.engine: Optional[Engine] = None
        self._load_environment()

    def _load_environment(self) -> None:
        """
        .env dosyasından ortam değişkenlerini yükler.
        """
        load_dotenv()

        # Gerekli ortam değişkenlerini kontrol et
        required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            raise ValueError(
                f"Eksik ortam değişkenleri: {', '.join(missing_vars)}. "
                "Lütfen .env dosyasını kontrol edin."
            )

    def get_connection_string(self) -> str:
        """
        PostgreSQL bağlantı string'ini oluşturur.
        Özel karakterleri URL encoding ile güvenli hale getirir.

        Returns:
            str: PostgreSQL bağlantı string'i
        """
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT')
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')

        # Kullanıcı adı ve şifreyi URL encoding yap (özel karakterler için)
        db_user_encoded = quote_plus(db_user)
        db_password_encoded = quote_plus(db_password)

        return f"postgresql://{db_user_encoded}:{db_password_encoded}@{db_host}:{db_port}/{db_name}"

    def create_engine(self) -> Engine:
        """
        SQLAlchemy engine oluşturur.

        Returns:
            Engine: SQLAlchemy engine nesnesi

        Raises:
            SQLAlchemyError: Bağlantı hatası durumunda
        """
        if self.engine is not None:
            return self.engine

        try:
            connection_string = self.get_connection_string()

            # Connection pool ayarları
            pool_size = int(os.getenv('DB_POOL_SIZE', 5))
            max_overflow = int(os.getenv('DB_MAX_OVERFLOW', 10))
            pool_timeout = int(os.getenv('DB_POOL_TIMEOUT', 30))
            pool_recycle = int(os.getenv('DB_POOL_RECYCLE', 3600))

            self.engine = create_engine(
                connection_string,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_timeout=pool_timeout,
                pool_recycle=pool_recycle,
                echo=os.getenv('DEBUG_MODE', 'False').lower() == 'true'
            )

            logger.info("Veritabanı bağlantısı başarıyla oluşturuldu.")
            return self.engine

        except SQLAlchemyError as e:
            logger.error(f"Veritabanı bağlantı hatası: {str(e)}")
            raise

    def test_connection(self) -> bool:
        """
        Veritabanı bağlantısını test eder.

        Returns:
            bool: Bağlantı başarılı ise True, değilse False
        """
        try:
            engine = self.create_engine()
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
            logger.info("Veritabanı bağlantı testi başarılı.")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Veritabanı bağlantı testi başarısız: {str(e)}")
            return False

    def get_engine(self) -> Engine:
        """
        Mevcut engine'i döndürür veya yoksa oluşturur.

        Returns:
            Engine: SQLAlchemy engine nesnesi
        """
        if self.engine is None:
            return self.create_engine()
        return self.engine

    def close(self) -> None:
        """
        Veritabanı bağlantısını kapatır.
        """
        if self.engine is not None:
            self.engine.dispose()
            logger.info("Veritabanı bağlantısı kapatıldı.")
            self.engine = None

    def get_table_names(self, schema: str = None) -> list:
        """
        Veritabanındaki tüm tablo isimlerini getirir.

        Args:
            schema: Schema adı (None ise .env'den alınır)

        Returns:
            list: Tablo isimleri listesi
        """
        try:
            if schema is None:
                schema = os.getenv('DB_SCHEMA', 'public')

            engine = self.get_engine()
            with engine.connect() as connection:
                result = connection.execute(text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = :schema"
                ), {"schema": schema})
                return [row[0] for row in result]
        except SQLAlchemyError as e:
            logger.error(f"Tablo isimleri alınırken hata: {str(e)}")
            return []

    def check_table_exists(self, table_name: str, schema: str = None) -> bool:
        """
        Belirtilen tablonun var olup olmadığını kontrol eder.

        Args:
            table_name: Kontrol edilecek tablo ismi
            schema: Schema adı (None ise .env'den alınır)

        Returns:
            bool: Tablo varsa True, yoksa False
        """
        try:
            if schema is None:
                schema = os.getenv('DB_SCHEMA', 'public')

            engine = self.get_engine()
            with engine.connect() as connection:
                result = connection.execute(text(
                    "SELECT EXISTS ("
                    "SELECT FROM information_schema.tables "
                    "WHERE table_schema = :schema "
                    "AND table_name = :table_name"
                    ")"
                ), {"schema": schema, "table_name": table_name})
                return result.fetchone()[0]
        except SQLAlchemyError as e:
            logger.error(f"Tablo kontrolü sırasında hata: {str(e)}")
            return False


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """
    Global DatabaseManager instance'ını döndürür (singleton pattern).

    Returns:
        DatabaseManager: DatabaseManager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


if __name__ == "__main__":
    # Test amaçlı kullanım
    db = DatabaseManager()

    print("Veritabanı bağlantısı test ediliyor...")
    if db.test_connection():
        print("✓ Bağlantı başarılı!")

        print("\nMevcut tablolar:")
        tables = db.get_table_names()
        for table in tables:
            print(f"  - {table}")
    else:
        print("✗ Bağlantı başarısız!")

    db.close()
