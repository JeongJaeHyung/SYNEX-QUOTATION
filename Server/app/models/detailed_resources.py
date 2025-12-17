# app/models/detailed_resources.py

from sqlalchemy import Column, String, Integer, Text, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from database import Base
from db_types import UUID

class DetailedResources(Base):
    __tablename__ = "detailed_resources"
    
    # PK, FK to detailed
    detailed_id = Column(UUID, primary_key=True)
    
    # PK
    major = Column(String(30), primary_key=True)
    minor = Column(String(50), primary_key=True)
    
    # Data Columns
    unit = Column(String(10), nullable=False)
    solo_price = Column(Integer, nullable=False)
    compare = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    detailed = relationship("Detailed", back_populates="detailed_resources")
    
    # 복합 FK 제약 조건
    __table_args__ = (
        ForeignKeyConstraint(
            ['detailed_id'],
            ['detailed.id'],
            ondelete='CASCADE'
        ),
    )

    def __repr__(self):
        return f"<DetailedResources(detailed_id='{self.detailed_id}', major='{self.major}', minor='{self.minor}')>"