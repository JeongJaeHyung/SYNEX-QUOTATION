import os
import requests
import svgwrite
from dotenv import load_dotenv

# ----------------------------------------------------------------
# 1. API 설정 및 환경 변수 로드
# ----------------------------------------------------------------
# .env 파일 로드
server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
load_dotenv(os.path.join(server_dir, ".env"))

# API 서버의 기본 URL 설정
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8005") 

# [가정] DB 스키마 정보를 가져오는 API 엔드포인트
SCHEMA_API_URL = f"{BASE_URL}/api/v1/admin/db-schema"
OUTPUT_FILE = 'database_erd_from_api.svg'

def fetch_db_schema_from_api():
    """
    가상의 API 엔드포인트를 호출하여 DB 스키마 정보를 JSON으로 가져옵니다.
    """
    print(f"🔗 Fetching DB schema from: GET {SCHEMA_API_URL}")
    try:
        # 실제 API 호출
        response = requests.get(SCHEMA_API_URL, timeout=10)
        response.raise_for_status()
        
        # API 응답 JSON 데이터를 반환합니다.
        # 응답 구조는 아래 HARDCODED_SCHEMA를 참조하십시오.
        return response.json() 
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error fetching schema: {e}")
        print("  ⚠️ 경고: API 호출에 실패했습니다. 하드코딩된 더미 데이터로 ERD를 생성합니다.")
        # API 호출 실패 시, 원래 코드의 더미 데이터 반환
        return HARDCODED_SCHEMA


# ----------------------------------------------------------------
# 2. API 스키마 응답 구조 (하드코딩된 더미 데이터)
# ----------------------------------------------------------------
# 실제 API에서 이와 유사한 JSON 구조를 반환한다고 가정합니다.
HARDCODED_SCHEMA = {
    "tables": {
        "ACCOUNT": ["id (PK)", "pwd", "name", "department", "position", "phone_number", "e_mail"],
        "MAKER": ["id (PK)", "name", "created_at", "updated_at"],
        "RESOURCES": ["id (PK)", "maker_id (PK, FK)", "name", "unit", "solo_price", "major", "minor"],
        "CERTIFICATION": ["id (PK)", "resources_id (FK)", "maker_id (FK)", "ul", "ce", "kc", "etc"],
        "MACHINE": ["id (PK)", "name", "manufacturer", "client", "price", "description"],
        "MACHINE_RESOURCES": ["machine_id (PK, FK)", "maker_id (PK, FK)", "resources_id (PK, FK)", "quantity", "solo_price"]
    },
    # 관계 정보도 API에서 가져온다고 가정합니다.
    "relations": [
        ("MAKER", "RESOURCES"),
        ("RESOURCES", "CERTIFICATION"),
        ("MACHINE", "MACHINE_RESOURCES"),
        ("RESOURCES", "MACHINE_RESOURCES"),
    ]
}


def create_erd_svg_from_api():
    """
    API에서 가져온 스키마 정보를 바탕으로 ERD SVG 파일을 생성합니다.
    """
    # 1. API에서 스키마 데이터 로드
    schema_data = fetch_db_schema_from_api()
    
    tables = schema_data.get("tables", {})
    relations = schema_data.get("relations", [])
    
    if not tables:
        print("❌ 스키마 데이터(테이블 목록)를 가져올 수 없습니다. ERD 생성을 중단합니다.")
        return

    # 캔버스 설정
    dwg = svgwrite.Drawing(OUTPUT_FILE, profile='full', size=(1200, 1000))
    
    # 스타일 정의 (이 부분은 동적으로 변경할 필요가 없으므로 유지)
    dwg.defs.add(dwg.style("""
        .table-box { fill: #f0f0f0; stroke: #333; stroke-width: 2px; }
        .table-title { font-family: sans-serif; font-size: 16px; font-weight: bold; text-anchor: middle; }
        .table-text { font-family: sans-serif; font-size: 12px; }
        .line { stroke: #666; stroke-width: 1px; fill: none; marker-end: url(#arrow); }
    """))
    
    # 화살표 마커
    marker = dwg.marker(insert=(10, 5), size=(10, 10), orient='auto', id='arrow')
    marker.add(dwg.path(d='M0,0 L10,5 L0,10 L3,5 z', fill='#666'))
    dwg.defs.add(marker)

    # 위치 설정 (하드코딩된 위치를 사용하거나 동적으로 계산해야 함)
    # API가 위치 정보는 제공하지 않으므로 기존 위치를 사용합니다.
    positions = {
        "ACCOUNT": (50, 50),
        "MAKER": (350, 50),
        "MACHINE": (650, 50),
        "RESOURCES": (350, 300),
        "CERTIFICATION": (50, 300),
        "MACHINE_RESOURCES": (650, 300)
    }
    
    box_width = 250
    line_height = 20
    header_height = 30

    # 테이블 그리기
    for name, cols in tables.items():
        x, y = positions.get(name) # API에서 가져온 테이블만 그립니다.
        
        if not (x and y):
            print(f"⚠️ 경고: 테이블 '{name}'에 대한 위치 정보가 정의되지 않아 생략합니다.")
            continue
            
        box_height = header_height + len(cols) * line_height + 10
        
        # 박스
        dwg.add(dwg.rect(insert=(x, y), size=(box_width, box_height), class_="table-box"))
        
        # 제목
        dwg.add(dwg.text(name, insert=(x + box_width/2, y + 20), class_="table-title"))
        dwg.add(dwg.line(start=(x, y + header_height), end=(x + box_width, y + header_height), stroke="#333", stroke_width=1))
        
        # 컬럼
        for i, col in enumerate(cols):
            dwg.add(dwg.text(col, insert=(x + 10, y + header_height + 15 + i * line_height), class_="table-text"))

    # 관계선 그리기 (API에서 가져온 relations 사용)
    def draw_rel(t1, t2):
        x1, y1 = positions.get(t1)
        x2, y2 = positions.get(t2)
        
        if not (x1 and y1 and x2 and y2):
            return

        # 테이블 높이 계산
        h1 = header_height + len(tables[t1]) * line_height + 10
        
        # 박스 중심 연결
        start = (x1 + box_width/2, y1 + h1)
        end = (x2 + box_width/2, y2)
        
        if y1 == y2: # 같은 라인 (옆으로)
             start = (x1 + box_width, y1 + 50)
             end = (x2, y2 + 50)
        
        dwg.add(dwg.line(start=start, end=end, class_="line"))

    for t1, t2 in relations:
        draw_rel(t1, t2)

    dwg.save()
    print(f"SVG generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    create_erd_svg_from_api()