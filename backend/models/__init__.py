# backend/models/__init__.py

from backend.database import Base

# 순서 중요! FK 참조되는 테이블이 먼저 와야 함
from backend.models.general import General
from backend.models.folder import Folder  # ← 추가!

from backend.models.maker import Maker
from backend.models.resources import Resources
from backend.models.certification import Certification
from backend.models.machine import Machine
from backend.models.machine_resources import MachineResources

from backend.models.price_compare import PriceCompare
from backend.models.price_compare_machine import PriceCompareMachine
from backend.models.price_compare_resources import PriceCompareResources

from backend.models.detailed import Detailed
from backend.models.detailed_resources import DetailedResources

from backend.models.header import Header
from backend.models.header_resources import HeaderResources

from backend.models.account import Account
from backend.models.role import Role
from backend.models.permission import Permission
from backend.models.role_permission import RolePermission

__all__ = [
    "Base",
    "General",
    "Folder",  # ← 추가!
    "Maker",
    "Resources",
    "Certification",
    "Machine",
    "MachineResources",
    "PriceCompare",
    "PriceCompareMachine",
    "PriceCompareResources",
    "Detailed",
    "DetailedResources",
    "Header",
    "HeaderResources",
    "Account",
    "Role",
    "Permission",
    "RolePermission"
]