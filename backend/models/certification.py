# SYNEX+QUOTATION/Server/app/models/certification.py
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKeyConstraint, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database import Base

class Certification(Base):
    __tablename__ = "certification"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 복합 FK
    resources_id = Column(String(6), nullable=False)
    maker_id = Column(String(4), nullable=False)
    
    # 인증 정보
    ul = Column(Boolean, nullable=False, default=False)
    ce = Column(Boolean, nullable=False, default=False)
    kc = Column(Boolean, nullable=False, default=False)
    etc = Column(Text, nullable=True)
    
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships (복합 FK)
    resource = relationship(
        "Resources",
        back_populates="certification",
        foreign_keys=[resources_id, maker_id],
        primaryjoin="and_(Certification.resources_id==Resources.id, Certification.maker_id==Resources.maker_id)"
    )
    
    # 복합 FK 제약조건
    __table_args__ = (
        ForeignKeyConstraint(
            ['resources_id', 'maker_id'],
            ['resources.id', 'resources.maker_id']
        ),
    )
    
    def __repr__(self):
        return f"<Certification(id={self.id}, resources_id='{self.resources_id}', maker_id='{self.maker_id}')>"