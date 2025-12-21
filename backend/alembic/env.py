from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
from pathlib import Path

# 1. 경로 설정: 프로젝트 루트를 sys.path에 추가하여 'backend' 패키지를 인식하게 함
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

# 2. 모델 import: 모든 모델이 등록된 __init__.py를 가져옵니다.
from backend.database import Base
# 모든 모델을 임포트해야 Alembic이 테이블 변화를 감지합니다.
import backend.models 

# 3. Alembic 설정 객체
config = context.config

# 4. Logging 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 5. 메타데이터 설정
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Offline 모드에서 마이그레이션 실행"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Online 모드에서 마이그레이션 실행"""
    # alembic.ini의 설정을 사용하여 엔진 생성
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # 이 부분을 추가해!
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()