# tools/register/main.py
import asyncio
import sys
import os

# 프로젝트 루트 경로를 sys.path에 추가 (임포트 에러 방지)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 절대 경로 임포트로 변경
from tools.register.makers import main as register_makers
from tools.register.parts import main as register_parts
from tools.register.templates import main as register_templates

async def run_all():
    print("=== 1. 제조사 등록 시작 ===")
    # 만약 makers.py의 main이 일반 함수라면 그냥 호출, 
    # async 함수라면 await 호출이 필요합니다.
    # 여기서는 이전 코드 기준에 맞춰 작성합니다.
    await register_makers() 

    print("\n=== 2. 부품 마스터 등록 시작 ===")
    await register_parts()

    print("\n=== 3. 템플릿 등록 시작 ===")
    await register_templates()

    print("\n✅ 모든 데이터 등록 공정이 완료되었습니다.")

if __name__ == "__main__":
    asyncio.run(run_all())