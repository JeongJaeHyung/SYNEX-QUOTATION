# Server/app/db_types.py
# 크로스 플랫폼 UUID 타입 - PostgreSQL과 SQLite 모두 지원

import os
import uuid as uuid_module
from sqlalchemy import String, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PGUUID


class UUID(TypeDecorator):
    """
    플랫폼 독립적인 UUID 타입.

    - PostgreSQL: 네이티브 UUID 타입 사용 (as_uuid=True)
    - SQLite: String(36)으로 저장, UUID 객체로 변환하여 반환

    사용법:
        from db_types import UUID
        id = Column(UUID, primary_key=True, default=uuid.uuid4)
    """
    impl = String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """데이터베이스 방언에 따라 적절한 타입 반환"""
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PGUUID(as_uuid=True))
        return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        """Python → DB 저장 시 변환"""
        if value is None:
            return value

        if dialect.name == 'postgresql':
            # PostgreSQL: UUID 객체 그대로 전달
            if isinstance(value, str):
                return uuid_module.UUID(value)
            return value
        else:
            # SQLite: 문자열로 변환
            if isinstance(value, uuid_module.UUID):
                return str(value)
            return value

    def process_result_value(self, value, dialect):
        """DB → Python 읽기 시 변환"""
        if value is None:
            return value

        if dialect.name == 'postgresql':
            # PostgreSQL: 이미 UUID 객체로 반환됨
            return value
        else:
            # SQLite: 문자열을 UUID 객체로 변환
            if isinstance(value, str):
                return uuid_module.UUID(value)
            return value
