
import sys
import os
import json
from dotenv import load_dotenv

# Server 디렉토리 path 추가
server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Server', 'app')
sys.path.append(server_dir)

# Load env
load_dotenv(os.path.join(server_dir, "..", ".env"))

# [Fix] Override DB_HOST for local execution
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"

from database import SessionLocal
from models.machine import Machine
from models.machine_resources import MachineResources
from models.resources import Resources

def check_data():
    db = SessionLocal()
    try:
        # 1. 템플릿 찾기
        template = db.query(Machine).filter(Machine.name.like("%1st EL_1st Fill%")).first()
        if not template:
            print("Template not found!")
            return

        print(f"Template: {template.name} (ID: {template.id})")

        # 2. 리소스 조회 (인건비만)
        resources = db.query(MachineResources).filter(
            MachineResources.machine_id == template.id,
            MachineResources.maker_id == 'LABOR'
        ).all()

        print(f"Found {len(resources)} labor resources.")

        for mr in resources:
            # 3. 연결된 Resources(마스터) 데이터 조회
            part = db.query(Resources).filter(
                Resources.maker_id == mr.maker_id,
                Resources.id == mr.resources_id
            ).first()
            
            print("-" * 40)
            print(f"Resource ID: {mr.resources_id}")
            print(f"  [MachineResources] Price: {mr.solo_price}, Qty: {mr.quantity}")
            print(f"  [MachineResources] Display Model Name: '{mr.display_model_name}'")
            
            if part:
                print(f"  [Master Part] ID: {part.id}")
                print(f"  [Master Part] Name: '{part.name}'")
                print(f"  [Master Part] Minor: '{part.minor}'")
                print(f"  [Master Part] Major: '{part.major}'")
            else:
                print("  [Master Part] NOT FOUND in Resources table!")

    finally:
        db.close()

if __name__ == "__main__":
    check_data()
