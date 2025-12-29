# backend/core/database.py
import os
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. 절대 경로로 프로젝트 루트 찾기
# 현재 파일: .../backend/core/database.py -> .parent(core) -> .parent(backend) -> .parent(root)
BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "jlt_quotation.db"

# 폴더 자동 생성
DB_DIR.mkdir(exist_ok=True)

# 2. SQLite URL 설정
# 리눅스 환경에서는 sqlite:////절대경로 (슬래시 4개)가 가장 안전합니다.
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# [중요] 앱 실행 시 터미널에서 이 경로가 아까 alembic이 건드린 경로와 같은지 확인하세요!
print(f"[*] 연결된 실제 DB 경로: {DB_PATH}")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)


# SQLite 외래키 활성화
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
