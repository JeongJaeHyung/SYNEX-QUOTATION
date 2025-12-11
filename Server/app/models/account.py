# app/models/account.py
from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Account(Base):
    __tablename__ = "account"
    
    account_id = Column(String(25), primary_key=True)
    password = Column(String(255), nullable=False)
    name = Column(String(10), nullable=False)
    department = Column(String(25), nullable=False)
    position = Column(String(25), nullable=False)
    phone_number = Column(String(11), nullable=False)
    e_mail = Column(String(255), nullable=False, unique=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    machines = relationship("Machine", back_populates="account")  # 추가!
    
    def __repr__(self):
        return f"<Account(account_id='{self.account_id}', name='{self.name}', department='{self.department}')>"