# app/models/resources.py
from sqlalchemy import Column, String, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database import Base

class Resources(Base):
    __tablename__ = "resources"
    
    # ✅ PK는 이 2개로 압축
    id = Column(String(6), primary_key=True)
    maker_id = Column(String(4), ForeignKey("maker.id"), primary_key=True)

    # 일반 컬럼으로 변경
    major = Column(String(50), nullable=False)
    minor = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)

    unit = Column(String(10), nullable=False)
    solo_price = Column(Integer, nullable=False)
    display_order = Column(Integer, nullable=False) 
    
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    maker = relationship("Maker", back_populates="resources")
    certification = relationship("Certification", back_populates="resource", uselist=False)
    
    def __repr__(self):
        return f"<Resources(id='{self.id}', maker_id='{self.maker_id}', name='{self.name}')>"