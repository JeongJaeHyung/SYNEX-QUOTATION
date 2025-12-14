# app/database.py
#
# 데이터베이스 연결 및 세션 관리를 위한 모듈입니다.
# - 환경 변수를 사용하여 PostgreSQL 데이터베이스에 연결합니다.
# - SQLAlchemy 엔진 및 세션 팩토리를 설정합니다.
# - FastAPI 의존성 주입(Dependency Injection)을 위한 `get_db` 헬퍼 함수를 제공합니다.
#

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base # ORM 모델의 베이스 클래스
from sqlalchemy.orm import sessionmaker # 세션 생성 팩토리
from urllib.parse import quote_plus # URL 인코딩 (비밀번호 등 특수문자 처리)
import os # 환경 변수 접근을 위함

# --- 데이터베이스 연결 설정 ---
# 환경 변수에서 데이터베이스 접속 정보를 가져옵니다.
# 환경 변수가 설정되어 있지 않으면 기본값(개발용)을 사용합니다.
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost") # Docker 컨테이너 내부에서는 'synex-postgres-db'
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "synex_quotation_db")

# 데이터베이스 비밀번호에 특수문자가 포함될 경우를 대비하여 URL 인코딩을 수행합니다.
DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD)

# PostgreSQL 연결 URL을 생성합니다.
# 형식: postgresql://사용자명:비밀번호@호스트:포트/데이터베이스명
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD_ENCODED}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 필수 환경 변수가 하나라도 누락되면 에러를 발생시킵니다.
if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    raise ValueError("데이터베이스 설정이 불완전합니다. 환경 변수를 확인해주세요.")

# --- SQLAlchemy 엔진 및 세션 설정 ---

# 데이터베이스 엔진을 생성합니다.
# - pool_pre_ping=True: 연결 풀에서 연결을 사용하기 전에 유효성 검사.
# - pool_size=10: 연결 풀에 유지할 최소 연결 개수.
# - max_overflow=20: pool_size 초과 시 최대로 허용할 추가 연결 개수.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True, # 연결 유효성 검사 (끊어진 연결 방지)
    pool_size=10,       # DB 연결 풀 사이즈
    max_overflow=20     # 풀 사이즈 초과 시 최대 오버플로우 연결 수
)

# 세션 팩토리를 생성합니다.
# - autocommit=False: 트랜잭션 수동 커밋 필요 (기본값)
# - autoflush=False: 변경사항 자동 플러시 비활성화 (명시적 플러시 필요)
# - bind=engine: 생성된 엔진에 바인딩
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 모델을 정의하기 위한 베이스 클래스입니다.
# 모든 SQLAlchemy 모델 클래스는 이 Base를 상속받아야 합니다.
Base = declarative_base()

# --- 의존성 주입을 위한 헬퍼 함수 ---

def get_db():
    """
    FastAPI의 의존성 주입(Dependency Injection)을 위한 제너레이터 함수입니다.
    요청마다 새로운 데이터베이스 세션을 생성하고, 요청이 완료되면 세션을 닫습니다.
    """
    db = SessionLocal() # 새로운 세션 생성
    try:
        yield db # 세션을 컨트롤러/API 엔드포인트에 제공
    finally:
        db.close() # 요청 완료 후 세션 반환/닫기
