# app/__init__.py

from backend.database import Base

# 기존 모델
from .maker import Maker
from .resources import Resources
from .certification import Certification
from .machine import Machine
from .machine_resources import MachineResources
from .account import Account
from .role import Role
from .permission import Permission
from .role_permission import role_permission 
from .general import General
from .header import Quotation
from .header_resources import QuotationResources
from .detailed import Detailed
from .detailed_resources import DetailedResources
from .price_compare import PriceCompare
from .price_compare_resources import PriceCompareResources
from .price_compare_machine import PriceCompareMachine

__all__ = [
    "Base", 
    
    # 기존 모델
    "Maker", 
    "Resources", 
    "Certification",
    "Machine",
    "MachineResources",
    "Account",
    "Role",
    "Permission",
    "role_permission",
    "General",
    "Quotation",
    "QuotationResources",
    "Detailed",
    "DetailedResources",
    "PriceCompare",
    "PriceCompareResources",
    "PriceCompareMachine",
]