# SYNEX+QUOTATION/Server/app/database.py
# 듀얼 모드 지원: PostgreSQL (개발) / SQLite (데스크톱 배포)

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
import os
import sys

# ============================================================
# 데이터베이스 모드 설정
# - "postgresql": 웹 서버 모드 (기존)
# - "sqlite": 데스크톱 앱 모드
# ============================================================
DB_MODE = os.getenv("DB_MODE", "sqlite")  # 기본값: sqlite (데스크톱)


def get_base_path():
    """PyInstaller frozen 앱 또는 개발 환경의 기본 경로 반환"""
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 exe 실행 시
        return os.path.dirname(sys.executable)
    else:
        # 개발 환경
        return os.path.dirname(os.path.abspath(__file__))


if DB_MODE == "postgresql":
    # ============================================================
    # PostgreSQL 모드 (웹 서버)
    # ============================================================
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "synex_quotation_db")

    # 비밀번호 URL 인코딩 (특수문자 처리)
    DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD)

    # DATABASE_URL 생성 (pg8000 드라이버 사용 - 32-bit Python 호환)
    DATABASE_URL = f"postgresql+pg8000://{DB_USER}:{DB_PASSWORD_ENCODED}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
        raise ValueError("Database configuration is incomplete")

    # Engine 생성
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

else:
    # ============================================================
    # SQLite 모드 (데스크톱 앱)
    # ============================================================
    BASE_DIR = get_base_path()
    DATA_DIR = os.path.join(BASE_DIR, "data")

    # data 폴더 생성
    os.makedirs(DATA_DIR, exist_ok=True)

    DB_PATH = os.path.join(DATA_DIR, "synex_quotation.db")
    DATABASE_URL = f"sqlite:///{DB_PATH}"

    # Engine 생성 (SQLite 전용 설정)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # 멀티스레드 허용
        echo=False
    )

    # SQLite Foreign Key 활성화 (기본적으로 비활성화됨)
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# ============================================================
# 공통 설정
# ============================================================
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI 의존성 주입용 DB 세션 생성기"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    데이터베이스 테이블 초기화 (SQLite 모드에서 사용)
    모든 모델을 import한 후 호출해야 함
    """
    Base.metadata.create_all(bind=engine)
