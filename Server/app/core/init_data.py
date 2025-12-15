import sys
import os

# [핵심 수정] 현재 파일(init_data.py)의 부모의 부모 경로(/app)를 시스템 경로에 추가
# 이렇게 해야 'database'와 'models'를 찾을 수 있습니다.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database import SessionLocal
from models import Role, Permission 

def init_db():
    db = SessionLocal()
    try:
        print("🔄 초기 데이터 주입 시작...")

        # ---------------------------------------------------------
        # 1. Permission 생성 (22개)
        # ---------------------------------------------------------
        resources = ["parts", "maker", "machine", "general", "account"]
        actions = ["create", "read", "update", "delete"]
        
        # 특수 권한 추가
        special_perms = [
            {"resource": "general", "action": "confirm"}, # 견적 확정
            {"resource": "machine", "action": "export"}   # 엑셀 다운로드
        ]

        all_permissions = []

        # 기본 CRUD
        for res in resources:
            for act in actions:
                perm = db.query(Permission).filter_by(resource=res, action=act).first()
                if not perm:
                    perm = Permission(resource=res, action=act, description=f"{res} {act}")
                    db.add(perm)
                    db.commit()
                    db.refresh(perm)
                all_permissions.append(perm)
        
        # 특수 권한
        for p in special_perms:
            perm = db.query(Permission).filter_by(resource=p["resource"], action=p["action"]).first()
            if not perm:
                perm = Permission(resource=p["resource"], action=p["action"], description="Special Permission")
                db.add(perm)
                db.commit()
                db.refresh(perm)
            all_permissions.append(perm)

        print(f"✅ Permission {len(all_permissions)}개 확인 완료.")

        # ---------------------------------------------------------
        # 2. Role 생성 (ADMIN, USER)
        # ---------------------------------------------------------
        roles_data = ["ADMIN", "USER"]
        roles_map = {}

        for r_name in roles_data:
            role = db.query(Role).filter_by(name=r_name).first()
            if not role:
                role = Role(name=r_name, description=f"System {r_name}")
                db.add(role)
                db.commit()
                db.refresh(role)
            roles_map[r_name] = role
        
        print("✅ Role (ADMIN, USER) 확인 완료.")

        # ---------------------------------------------------------
        # 3. Role - Permission 매핑
        # ---------------------------------------------------------
        admin_role = roles_map["ADMIN"]
        user_role = roles_map["USER"]

        # ADMIN: 모든 권한 부여
        if not admin_role.permissions:
            admin_role.permissions = all_permissions
            print("   -> ADMIN에게 모든 권한 부여 완료.")

        # USER: 'read', 'create' 권한만 부여 (예시)
        if not user_role.permissions:
            user_perms = [p for p in all_permissions if p.action in ["read", "create"]]
            user_role.permissions = user_perms
            print("   -> USER에게 Read/Create 권한 부여 완료.")

        db.commit()
        print("🎉 초기 데이터 주입 성공!")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()