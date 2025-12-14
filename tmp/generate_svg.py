
import svgwrite

def create_erd_svg():
    # 캔버스 설정
    dwg = svgwrite.Drawing('database_erd.svg', profile='full', size=(1200, 1000))
    
    # 스타일 정의
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

    # 테이블 데이터
    tables = {
        "ACCOUNT": ["id (PK)", "pwd", "name", "department", "position", "phone_number", "e_mail"],
        "MAKER": ["id (PK)", "name", "created_at", "updated_at"],
        "RESOURCES": ["id (PK)", "maker_id (PK, FK)", "name", "unit", "solo_price", "major", "minor"],
        "CERTIFICATION": ["id (PK)", "resources_id (FK)", "maker_id (FK)", "ul", "ce", "kc", "etc"],
        "MACHINE": ["id (PK)", "name", "manufacturer", "client", "price", "description"],
        "MACHINE_RESOURCES": ["machine_id (PK, FK)", "maker_id (PK, FK)", "resources_id (PK, FK)", "quantity", "solo_price"]
    }

    # 위치 설정 (간단한 그리드 배치)
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
        x, y = positions[name]
        box_height = header_height + len(cols) * line_height + 10
        
        # 박스
        dwg.add(dwg.rect(insert=(x, y), size=(box_width, box_height), class_="table-box"))
        
        # 제목
        dwg.add(dwg.text(name, insert=(x + box_width/2, y + 20), class_="table-title"))
        dwg.add(dwg.line(start=(x, y + header_height), end=(x + box_width, y + header_height), stroke="#333", stroke_width=1))
        
        # 컬럼
        for i, col in enumerate(cols):
            dwg.add(dwg.text(col, insert=(x + 10, y + header_height + 15 + i * line_height), class_="table-text"))

    # 관계선 그리기 (단순 직선)
    def draw_rel(t1, t2):
        x1, y1 = positions[t1]
        x2, y2 = positions[t2]
        
        # 박스 중심 연결
        start = (x1 + box_width/2, y1 + header_height + len(tables[t1]) * line_height + 10)
        end = (x2 + box_width/2, y2)
        
        if y1 == y2: # 같은 라인 (옆으로)
             start = (x1 + box_width, y1 + 50)
             end = (x2, y2 + 50)
        
        dwg.add(dwg.line(start=start, end=end, class_="line"))

    draw_rel("MAKER", "RESOURCES")
    draw_rel("RESOURCES", "CERTIFICATION")
    draw_rel("MACHINE", "MACHINE_RESOURCES")
    draw_rel("RESOURCES", "MACHINE_RESOURCES")

    dwg.save()
    print("SVG generated: database_erd.svg")

if __name__ == "__main__":
    create_erd_svg()
