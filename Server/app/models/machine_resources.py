# app/models/machine_resources.py
from sqlalchemy import Column, String, Integer, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from database import Base
from db_types import UUID


class MachineResources(Base):
    """
    'machine_resources' 테이블과 매핑되는 SQLAlchemy ORM 모델입니다.
    특정 견적서(Machine)에 포함된 자재(Resources)의 목록과 해당 견적에만 적용되는 상세 정보를 저장합니다.
    """
    __tablename__ = "machine_resources" # 매핑될 데이터베이스 테이블 이름
    
    # --- 복합 Primary Key 정의 (또한 복합 외래 키 역할) ---
    # 어떤 견적서의 어떤 자재인지를 고유하게 식별합니다.
    machine_id = Column(UUID, primary_key=True) # 견적서 ID (Machine 테이블의 id 참조)
    maker_id = Column(String(4), primary_key=True) # 자재의 제조사 ID (Resources 테이블의 maker_id 참조)
    resources_id = Column(String(6), primary_key=True) # 자재 ID (Resources 테이블의 id 참조)
    
    # --- 데이터 컬럼 정의 ---
    # 이 필드들은 견적서 작성 당시의 스냅샷 데이터를 저장하는 용도로 사용됩니다.
    # Resources 마스터 데이터가 변경되어도 견적서 내용은 영향을 받지 않습니다.
    solo_price = Column(Integer, nullable=False) # 이 견적서에서 이 자재에 적용된 단가
    quantity = Column(Integer, nullable=False, default=1) # 이 견적서에서 이 자재의 수량
    order_index = Column(Integer, nullable=False) # 견적서 내에서 자재 목록의 표시 순서

    # 템플릿/견적 화면에 표시될 때 사용되는 정보 (마스터 Resources와 다를 수 있음)
    display_major = Column(String(50), nullable=True) # 견적서 화면에 표시될 대분류
    display_minor = Column(String(50), nullable=True) # 견적서 화면에 표시될 중분류
    display_model_name = Column(String(100), nullable=True) # 견적서 화면에 표시될 모델명/규격
    display_maker_name = Column(String(100), nullable=True) # 견적서 화면에 표시될 제조사명
    display_unit = Column(String(10), nullable=True) # 견적서 화면에 표시될 단위
    
    # --- 관계 정의 ---
    # MachineResources와 Machine 간의 N:1 관계 (MachineResources는 하나의 Machine에 속함)
    machine = relationship("Machine", back_populates="machine_resources")
    # MachineResources와 Resources 간의 N:1 관계 (MachineResources는 하나의 Resources를 참조)
    resource = relationship(
        "Resources",
        foreign_keys=[maker_id, resources_id], # 복합 외래 키 지정
        primaryjoin="and_(MachineResources.maker_id==Resources.maker_id, MachineResources.resources_id==Resources.id)"
    )
    
    # --- 복합 외래 키 제약조건 ---
    # machine 테이블의 id를 외래 키로 참조하며, Machine 삭제 시 MachineResources도 함께 삭제됩니다 (CASCADE).
    # resources 테이블의 (maker_id, id) 복합 키를 외래 키로 참조합니다.
    __table_args__ = (
        ForeignKeyConstraint(
            ['machine_id'],
            ['machine.id'],
            ondelete='CASCADE' # Machine 삭제 시 연관된 MachineResources도 삭제
        ),
        ForeignKeyConstraint(
            ['maker_id', 'resources_id'],
            ['resources.maker_id', 'resources.id']
        ),
    )
    
    def __repr__(self):
        """객체를 문자열로 표현할 때 사용됩니다."""
        return f"<MachineResources(machine_id='{self.machine_id}', maker_id='{self.maker_id}', resources_id='{self.resources_id}', quantity={self.quantity})>"