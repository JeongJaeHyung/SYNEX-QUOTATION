# app/models/machine_resources.py
from sqlalchemy import Column, ForeignKeyConstraint, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database import Base


class MachineResources(Base):
    __tablename__ = "machine_resources"

    machine_id = Column(UUID(as_uuid=True), primary_key=True)
    # 부모 PK와 일치하는 2개 컬럼
    resources_id = Column(String(6), primary_key=True)
    maker_id = Column(String(4), primary_key=True)

    solo_price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    order_index = Column(Integer, nullable=False)

    # Resources의 나머지는 스냅샷 정보로 유지 가능
    display_major = Column(String(50), nullable=True)
    display_minor = Column(String(50), nullable=True)
    display_model_name = Column(String(100), nullable=True)
    display_maker_name = Column(String(100), nullable=True)
    display_unit = Column(String(10), nullable=True)

    machine = relationship("Machine", back_populates="machine_resources")

    # 2개 컬럼으로 관계 설정
    resource = relationship(
        "Resources",
        foreign_keys=[resources_id, maker_id],
        primaryjoin="and_(MachineResources.resources_id==Resources.id, MachineResources.maker_id==Resources.maker_id)",
    )

    __table_args__ = (
        ForeignKeyConstraint(["machine_id"], ["machine.id"], ondelete="CASCADE"),
        # 부모(Resources) PK 순서인 (id, maker_id)에 정확히 맞춤
        ForeignKeyConstraint(
            ["resources_id", "maker_id"], ["resources.id", "resources.maker_id"]
        ),
    )
