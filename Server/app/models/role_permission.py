from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from database import Base

# Association Table (클래스가 아닌 Table 객체로 정의)
role_permission = Table(
    'role_permission',
    Base.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('role.id', ondelete="CASCADE"), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permission.id', ondelete="CASCADE"), primary_key=True)
)