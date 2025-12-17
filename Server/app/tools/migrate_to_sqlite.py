# SYNEX+QUOTATION/Server/app/tools/migrate_to_sqlite.py
# PostgreSQL -> SQLite 데이터 마이그레이션 도구
#
# 사용법:
#   1. PostgreSQL 환경변수 설정 (.env 파일 또는 직접 설정)
#   2. python tools/migrate_to_sqlite.py 실행
#   3. data/synex_quotation.db 파일 생성됨

import os
import sys

# 부모 디렉토리를 경로에 추가 (app 폴더 기준 실행을 위함)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


def migrate():
    """PostgreSQL에서 SQLite로 데이터 마이그레이션"""

    # ============================================================
    # 1. PostgreSQL 연결 (소스)
    # ============================================================
    print("[Migration] PostgreSQL 연결 중...")

    # 환경변수에서 PostgreSQL 설정 가져오기
    from urllib.parse import quote_plus

    PG_USER = os.getenv("DB_USER", "postgres")
    PG_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    PG_HOST = os.getenv("DB_HOST", "localhost")
    PG_PORT = os.getenv("DB_PORT", "5432")
    PG_NAME = os.getenv("DB_NAME", "synex_quotation_db")

    PG_PASSWORD_ENCODED = quote_plus(PG_PASSWORD)
    # pg8000 드라이버 사용 (순수 Python, 32-bit 호환)
    PG_URL = f"postgresql+pg8000://{PG_USER}:{PG_PASSWORD_ENCODED}@{PG_HOST}:{PG_PORT}/{PG_NAME}"

    pg_engine = create_engine(PG_URL)
    PGSession = sessionmaker(bind=pg_engine)
    pg_session = PGSession()

    print(f"[Migration] PostgreSQL 연결 성공: {PG_HOST}:{PG_PORT}/{PG_NAME}")

    # ============================================================
    # 2. SQLite 연결 (대상)
    # ============================================================
    print("[Migration] SQLite 연결 중...")

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    os.makedirs(DATA_DIR, exist_ok=True)

    SQLITE_PATH = os.path.join(DATA_DIR, "synex_quotation.db")
    SQLITE_URL = f"sqlite:///{SQLITE_PATH}"

    sqlite_engine = create_engine(
        SQLITE_URL,
        connect_args={"check_same_thread": False}
    )

    # SQLite Foreign Key 활성화
    @event.listens_for(sqlite_engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    SQLiteSession = sessionmaker(bind=sqlite_engine)
    sqlite_session = SQLiteSession()

    print(f"[Migration] SQLite 파일: {SQLITE_PATH}")

    # ============================================================
    # 3. 모델 import 및 테이블 생성
    # ============================================================
    print("[Migration] 모델 로드 및 테이블 생성 중...")

    from database import Base
    from models import (
        Maker, Resources, Certification,
        Machine, MachineResources,
        Account, Role, Permission, role_permission,
        General, Quotation, QuotationResources,
        Detailed, DetailedResources,
        PriceCompare, PriceCompareResources, PriceCompareMachine
    )

    # SQLite에 테이블 생성
    Base.metadata.create_all(bind=sqlite_engine)
    print("[Migration] SQLite 테이블 생성 완료")

    # ============================================================
    # 4. 데이터 마이그레이션 (FK 의존성 순서 중요!)
    # ============================================================
    migration_order = [
        # 1단계: 기본 테이블 (FK 없음)
        ("Maker", Maker),
        ("Role", Role),
        ("Permission", Permission),

        # 2단계: 1단계 테이블 참조
        ("Account", Account),
        ("Resources", Resources),

        # 3단계: Resources 참조
        ("Certification", Certification),

        # 4단계: 독립 테이블
        ("Machine", Machine),
        ("General", General),

        # 5단계: Machine 참조
        ("MachineResources", MachineResources),

        # 6단계: General 참조
        ("Quotation", Quotation),
        ("Detailed", Detailed),
        ("PriceCompare", PriceCompare),

        # 7단계: 복합 참조
        ("QuotationResources", QuotationResources),
        ("DetailedResources", DetailedResources),
        ("PriceCompareMachine", PriceCompareMachine),
        ("PriceCompareResources", PriceCompareResources),
    ]

    print("[Migration] 데이터 마이그레이션 시작...")

    total_records = 0

    for table_name, model_class in migration_order:
        try:
            records = pg_session.query(model_class).all()
            count = len(records)

            if count > 0:
                for record in records:
                    # 객체를 딕셔너리로 변환 후 새 객체 생성
                    # (세션 간 객체 이동 방지)
                    record_dict = {
                        c.name: getattr(record, c.name)
                        for c in record.__table__.columns
                    }
                    new_record = model_class(**record_dict)
                    sqlite_session.merge(new_record)

                sqlite_session.commit()
                total_records += count
                print(f"  [OK] {table_name}: {count}건 마이그레이션 완료")
            else:
                print(f"  [--] {table_name}: 데이터 없음")

        except Exception as e:
            sqlite_session.rollback()
            print(f"  [ERROR] {table_name}: {str(e)}")

    # role_permission 중계 테이블은 별도 처리
    try:
        from sqlalchemy import select
        rp_records = pg_session.execute(select(role_permission)).fetchall()
        if rp_records:
            for row in rp_records:
                sqlite_session.execute(
                    role_permission.insert().values(
                        role_id=row.role_id,
                        permission_id=row.permission_id
                    )
                )
            sqlite_session.commit()
            print(f"  [OK] role_permission: {len(rp_records)}건 마이그레이션 완료")
            total_records += len(rp_records)
        else:
            print(f"  [--] role_permission: 데이터 없음")
    except Exception as e:
        sqlite_session.rollback()
        print(f"  [ERROR] role_permission: {str(e)}")

    # ============================================================
    # 5. 정리
    # ============================================================
    pg_session.close()
    sqlite_session.close()

    print("=" * 50)
    print(f"[Migration] 마이그레이션 완료!")
    print(f"[Migration] 총 {total_records}건 이전됨")
    print(f"[Migration] SQLite 파일: {SQLITE_PATH}")
    print("=" * 50)


if __name__ == "__main__":
    migrate()
