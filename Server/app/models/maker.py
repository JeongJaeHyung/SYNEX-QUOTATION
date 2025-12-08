from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Maker(Base):
    __tablename__ = "maker"
    
    id = Column(String(4), primary_key=True)
    name = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    resources = relationship("Resources", back_populates="maker")
    
    def __repr__(self):
        return f"<Maker(id='{self.id}', name='{self.name}')>"