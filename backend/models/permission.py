from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database import Base

class Permission(Base):
    __tablename__ = "permission"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    resource = Column(String(50), nullable=False) # 예: machine
    action = Column(String(50), nullable=False)   # 예: create
    description = Column(String(255), nullable=True)

    # 중복 방지 (Resource + Action 조합은 유일해야 함)
    __table_args__ = (
        UniqueConstraint('resource', 'action', name='uq_permission_resource_action'),
    )

    def __repr__(self):
        return f"<Permission({self.resource}:{self.action})>"