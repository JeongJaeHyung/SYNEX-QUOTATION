# backend/models/role.py
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from backend.database import Base
# 💡 수정된 이름으로 임포트
from .role_permission import RolePermission

class Role(Base):
    __tablename__ = "role"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False) # ADMIN, USER
    description = Column(String(255), nullable=True)
    
    # Permission과의 다대다 관계 설정
    permissions = relationship(
        "Permission",
        secondary=RolePermission, # 💡 수정된 변수명 반영
        backref="roles"
    )

    def __repr__(self):
        return f"<Role({self.name})>"