import json
import os

import requests
from dotenv import load_dotenv

# ----------------------------------------------------------------
# 1. API 설정 및 환경 변수 로드
# ----------------------------------------------------------------
# .env 파일 로드
server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
load_dotenv(os.path.join(server_dir, ".env"))

# [중요] API 서버의 기본 URL 설정 (Swagger 파일 기반)
# 실제 환경에 맞게 IP 주소와 포트를 수정해야 합니다.
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8005")
SEARCH_KEYWORD = "1st EL_1st Fill"  # 검색할 템플릿 키워드

# ----------------------------------------------------------------
# 2. API 호출 함수 정의
# ----------------------------------------------------------------


def find_machine_id_by_name(keyword: str):
    """
    Machine 검색 API를 호출하여 Machine ID(UUID)를 찾습니다.
    """
    search_url = f"{BASE_URL}/api/v1/quotation/machine/search"

    # 템플릿 이름을 검색하는 쿼리 파라미터 (일반적으로 'q' 또는 'name' 사용)
    # 여기서는 'q'를 사용한다고 가정합니다.
    params = {"q": keyword}

    print(f"🔗 Searching for template: GET {search_url} with params={params}")

    try:
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생

        data = response.json()

        # 응답이 리스트를 포함하는 구조(예: {'items': [...]} 또는 리스트 자체)라고 가정
        machines = data.get("items", data)

        if not machines:
            return None, "No machines found."

        # 첫 번째 일치하는 템플릿 반환
        first_machine = machines[0]
        return first_machine.get("id"), first_machine.get("name")

    except requests.exceptions.RequestException as e:
        return None, f"API Error during search: {e}"


def get_machine_details(machine_id: str):
    """
    Machine 상세 정보 API를 호출하여 연결된 리소스 정보를 가져옵니다.
    """
    detail_url = f"{BASE_URL}/api/v1/quotation/machine/{machine_id}"

    print(f"🔗 Fetching details for ID {machine_id}: GET {detail_url}")

    try:
        response = requests.get(detail_url, timeout=10)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"❌ API Error during detail fetch: {e}")
        return None


# ----------------------------------------------------------------
# 3. 메인 검사 로직
# ----------------------------------------------------------------


def check_data_via_api():
    print("🔍 API를 통한 데이터 무결성/연결 검사 시작...\n")

    # 1. 템플릿 ID 찾기
    machine_id, machine_name = find_machine_id_by_name(SEARCH_KEYWORD)

    if not machine_id:
        print(f"❌ Template not found or API call failed: {machine_name}")
        return

    print(f"✅ Template Found: {machine_name}")
    print(f"   - ID: {machine_id}")

    # 2. 템플릿 상세 정보(리소스 포함) 가져오기
    machine_data = get_machine_details(machine_id)

    if not machine_data:
        print("❌ Failed to fetch machine details.")
        return

    # 3. 리소스 데이터 필터링 및 출력
    # 응답 JSON에 'resources'라는 키로 리스트가 있다고 가정합니다.
    resources = machine_data.get("resources", [])

    print(f"\n📊 Found {len(resources)} total resources linked to this machine.")

    labor_resources = [mr for mr in resources if mr.get("maker_id") == "LABOR"]

    print(f"   - Filtering for LABOR resources: {len(labor_resources)} found.")

    for mr in labor_resources:
        # MachineResources에 해당하는 스냅샷 데이터
        resource_id = mr.get("resources_id", "N/A")
        solo_price = mr.get("solo_price", 0)
        quantity = mr.get("quantity", 0)
        display_name = mr.get("display_model_name", "N/A")

        # Master Data (Resources)에 해당하는 정보가 중첩되어 있다고 가정합니다.
        part = mr.get("master_data")

        print("-" * 60)
        print("📌 Resource Link (MachineResources Snapshot)")
        print(f"   - Resource ID: {resource_id}")
        print(f"   - Snapshot Price: {solo_price:,}원")
        print(f"   - Quantity: {quantity}")
        print(f"   - Display Name: '{display_name}'")

        print("\n   🔗 Master Data (Resources Table via API)")
        if part:
            print("      - Found: ✅ YES")
            print(f"      - Name: '{part.get('name', 'N/A')}'")
            print(f"      - Major: '{part.get('major', 'N/A')}'")
            print(f"      - Minor: '{part.get('minor', 'N/A')}'")
            print(f"      - Current Master Price: {part.get('solo_price', 0):,}원")
        else:
            print("      - Found: ❌ NO (Orphaned Data or Missing Link)")
            print(
                f"      - Warning: 해당 리소스 ID({resource_id})의 마스터 정보가 API 응답에 누락되었습니다."
            )

    print("\n검사 종료.")


if __name__ == "__main__":
    check_data_via_api()
