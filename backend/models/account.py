from sqlalchemy import TIMESTAMP, Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database import Base


class Account(Base):
    __tablename__ = "account"

    id = Column(String(25), primary_key=True)
    pwd = Column(String(255), nullable=False)
    name = Column(String(10), nullable=False)
    department = Column(String(25), nullable=False)
    position = Column(String(25), nullable=False)
    phone_number = Column(String(11), nullable=False)
    e_mail = Column(String(255), nullable=False, unique=True)

    # [추가] Role 연결 (N:1)
    role_id = Column(UUID(as_uuid=True), ForeignKey("role.id"), nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    # [추가] 관계 설정
    role = relationship("Role", backref="accounts")

    def __repr__(self):
        return f"<Account(id='{self.id}', name='{self.name}')>"
