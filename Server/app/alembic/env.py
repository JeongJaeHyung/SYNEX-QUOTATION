from logging.config import fileConfig
from sqlalchemy import engine_from_config, create_engine
from sqlalchemy import pool
from alembic import context
from urllib.parse import quote_plus
import os
import sys

# 경로 설정
sys.path.insert(0, '/app')

# 모델 import
from database import Base
from models.category import Category
from models.maker import Maker
from models.resources import Resources
from models.certification import Certification
from models.machine import Machine
from models.machine_resources import MachineResources

# Alembic Config
config = context.config

# 환경변수에서 개별 값 가져오기
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "synex_quotation_db")

# 비밀번호 URL 인코딩 (특수문자 처리)
DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD)

# DATABASE_URL 생성
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD_ENCODED}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Logging 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 메타데이터
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,  # 직접 사용!
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    # 직접 engine 생성!
    connectable = create_engine(DATABASE_URL)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()