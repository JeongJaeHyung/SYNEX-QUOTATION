from sqlalchemy import Column, ForeignKey, Table
from database import Base
from db_types import UUID

# Association Table (클래스가 아닌 Table 객체로 정의)
role_permission = Table(
    'role_permission',
    Base.metadata,
    Column('role_id', UUID, ForeignKey('role.id', ondelete="CASCADE"), primary_key=True),
    Column('permission_id', UUID, ForeignKey('permission.id', ondelete="CASCADE"), primary_key=True)
)