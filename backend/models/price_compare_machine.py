# app/models/price_compare_machine.py

from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database import Base


class PriceCompareMachine(Base):
    __tablename__ = "price_compare_machine"

    # PK, FK to price_compare
    price_compare_id = Column(
        UUID(as_uuid=True),
        ForeignKey("price_compare.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # PK, FK to machine
    machine_id = Column(
        UUID(as_uuid=True),
        ForeignKey("machine.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Relationships
    price_compare = relationship(
        "PriceCompare", back_populates="price_compare_machines"
    )
    machine = relationship("Machine", back_populates="price_compare_machines")

    # 복합 FK 제약 조건
    __table_args__ = (
        ForeignKeyConstraint(
            ["price_compare_id"], ["price_compare.id"], ondelete="CASCADE"
        ),
        ForeignKeyConstraint(["machine_id"], ["machine.id"], ondelete="CASCADE"),
    )

    def __repr__(self):
        return f"<PriceCompareMachine(pc_id='{self.price_compare_id}', machine_id='{self.machine_id}')>"
