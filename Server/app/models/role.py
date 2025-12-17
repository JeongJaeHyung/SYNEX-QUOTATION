from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
import uuid
from database import Base
from db_types import UUID

# 중계 테이블 import
from .role_permission import role_permission

class Role(Base):
    __tablename__ = "role"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False) # ADMIN, USER
    description = Column(String(255), nullable=True)
    
    # Permission과의 다대다 관계 설정
    # "Permission"을 문자열로 넣어서 순환 참조 방지
    permissions = relationship(
        "Permission",
        secondary=role_permission,
        backref="roles"
    )

    def __repr__(self):
        return f"<Role({self.name})>"