import os

import requests
from dotenv import load_dotenv

# ----------------------------------------------------------------
# 1. API 설정 및 환경 변수 로드
# ----------------------------------------------------------------
# .env 파일 로드
server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
load_dotenv(os.path.join(server_dir, ".env"))

# API 서버의 기본 URL 설정
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8005")

# ----------------------------------------------------------------
# 2. 엑셀 관련 변수를 API 검색 키워드로 재활용
# ----------------------------------------------------------------
# 엑셀 시트 이름 대신, API로 조회할 템플릿의 검색 키워드로 사용
SEARCH_KEYWORD = "1st EL_1st Fill"
LABOR_MAKER_ID = "LABOR"

# ----------------------------------------------------------------
# 3. API 호출 함수 정의 (이전 답변에서 사용한 함수 재사용)
# ----------------------------------------------------------------


def find_machine_id_by_name(keyword: str):
    """Machine 검색 API를 호출하여 Machine ID를 찾습니다."""
    # Swagger 파일 기반 가정: GET /api/v1/quotation/machine/search
    search_url = f"{BASE_URL}/api/v1/quotation/machine/search"
    params = {"q": keyword}

    try:
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        machines = data.get("items", data)

        if not machines:
            return None, "No machines found."

        first_machine = machines[0]
        return first_machine.get("id"), first_machine.get("name")

    except requests.exceptions.RequestException as e:
        return None, f"API Error during search: {e}"


def get_machine_details(machine_id: str):
    """Machine 상세 정보 API를 호출하여 연결된 리소스 정보를 가져옵니다."""
    # Swagger 파일 기반 가정: GET /api/v1/quotation/machine/{machine_id}
    detail_url = f"{BASE_URL}/api/v1/quotation/machine/{machine_id}"

    try:
        response = requests.get(detail_url, timeout=10)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"❌ API Error during detail fetch: {e}")
        return None


# ----------------------------------------------------------------
# 4. API 데이터를 엑셀 형식으로 시뮬레이션하여 출력
# ----------------------------------------------------------------


def debug_sheet_raw_via_api():
    print(f"🔍 API 호출을 통해 '{SEARCH_KEYWORD}' 템플릿 데이터 시뮬레이션 시작...\n")

    machine_id, machine_name = find_machine_id_by_name(SEARCH_KEYWORD)

    if not machine_id:
        print(f"❌ 템플릿 ID를 찾을 수 없거나 API 연결 실패: {machine_name}")
        return

    # 템플릿 상세 정보(리소스 포함) 가져오기
    machine_data = get_machine_details(machine_id)

    if not machine_data:
        print("❌ 템플릿 상세 정보를 가져오지 못했습니다.")
        return

    resources = machine_data.get("resources", [])
    labor_resources = [mr for mr in resources if mr.get("maker_id") == LABOR_MAKER_ID]

    print(f"\n=== Template: {machine_name} API Data Dump ===")

    # 엑셀의 Row 1~5 시뮬레이션 (헤더 정보)
    # 실제 엑셀을 읽는 것이 아니므로 가상의 헤더 정보를 출력합니다.
    print(f"Row 1: ['[0]템플릿명', '[1]{machine_name}', '[2]ID', '[3]{machine_id}']")
    print("Row 2: ['[0]날짜', '[1]2025-12-15']")
    print("Row 3: ['[0]버전', '[1]1.0']")
    print("Row 4: [...] (생략)")
    print(
        "Row 5: ['[0]구분', '[1]품명', '[2]단위', '[3]수량', '[4]단가', '[5]금액'] (가정된 컬럼 헤더)"
    )

    print("\n--- Labor Section Check (API Data Output) ---")
    print(f"Total {len(labor_resources)} LABOR items found via API.")

    # 인건비가 있을법한 위치 (Rows 130~) 시뮬레이션
    base_row_index = 130  # 엑셀 시뮬레이션 시작 행 번호

    if not labor_resources:
        print(f"Row {base_row_index}부터 인건비 항목이 없습니다.")
        return

    # API 데이터를 엑셀의 특정 컬럼 인덱스에 매핑하여 출력 시뮬레이션
    for i, mr in enumerate(labor_resources, base_row_index):
        # Master Data가 응답에 포함되어 있다고 가정
        part = mr.get("master_data", {})

        # 엑셀 컬럼 인덱스에 매핑 (가정)
        # [0]구분, [1]품명, [3]수량, [4]단가
        row_data = {
            0: LABOR_MAKER_ID,  # 구분 (Maker ID)
            1: part.get("name", "N/A")
            or mr.get(
                "display_model_name", "N/A"
            ),  # 품명 (Master Name 또는 Display Name)
            3: mr.get("quantity", 0),  # 수량 (Snapshot Qty)
            4: mr.get("solo_price", 0),  # 단가 (Snapshot Price)
        }

        # 값이 있는 컬럼만 출력
        row_display = []
        for col_idx in sorted(row_data.keys()):
            cell_value = row_data[col_idx]
            # 금액 계산 시뮬레이션
            if col_idx == 5:
                # 금액 = 수량 * 단가
                total_price = row_data.get(3, 0) * row_data.get(4, 0)
                row_display.append(f"[{5}]{total_price:,}")

            if cell_value and col_idx != 5:
                row_display.append(f"[{col_idx}]{cell_value}")

        print(f"Row {i}: {', '.join(row_display)}")

        # 마스터 데이터 누락 시 무결성 검사 메시지 추가
        if not part:
            print(
                f"  [⚠️ WARNING]: Resource ID {mr.get('resources_id')}의 마스터 데이터가 API 응답에 누락되었습니다."
            )


if __name__ == "__main__":
    debug_sheet_raw_via_api()
