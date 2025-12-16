# register_parts.py (openpyxl 기반)
import json
import os
from openpyxl import load_workbook
import urllib.request
import urllib.error

# --- Configuration ---
API_URL = "http://localhost:8005/api/v1/parts"
EXCEL_FILE_PATH = "SYNEX+QUOTATION INFO (1).xlsx"
# 현재 엑셀: 1번 시트(0-based 0)가 parts
PARTS_SHEET_NAME = 0 

def clean_value(value):
    """Excel 필드 값을 정리하고 '공백', 'nan' 등을 빈 문자열("")로 변환합니다."""
    if value is None:
        return ""

    cleaned = str(value).strip()
    
    # ✅ 수정: '공백' 텍스트이거나 'nan', 'None', 또는 완전히 빈 문자열인 경우 모두 빈 문자열("") 반환
    if cleaned in ("공백", "nan", "None") or not cleaned:
        return ""
        
    return cleaned

def clean_maker_name(value):
    """Maker name은 '공백'을 ' '로 유지(제조사명 매칭용)."""
    if value is None:
        return ""

    cleaned = str(value).strip()
    if cleaned == "공백":
        return " "
    if cleaned in ("nan", "None") or not cleaned:
        return ""
    return cleaned

def get_parts_data_from_excel(excel_file_path, sheet_name):
    """Excel 파일을 읽어 Parts 등록에 필요한 JSON 형식의 리스트로 변환합니다."""
    data_list = []
    skipped_count = 0 
    
    if not os.path.exists(excel_file_path):
        print(f"오류: 파일 경로를 찾을 수 없습니다: {excel_file_path}")
        return [], 0

    try:
        wb = load_workbook(excel_file_path, data_only=True)
        ws = wb.worksheets[sheet_name] if isinstance(sheet_name, int) else wb[sheet_name]
    except Exception as e:
        print(f"오류: 엑셀 파일/시트({sheet_name}) 읽기 실패: {e}")
        return [], 0

    # 현재 parts 시트 헤더
    # Unit | 품목 | 모델명/규격 | 제조사 | UL | CE | KC | 기타 | 단위 | 단가
    required_cols = ['Unit', '품목', '모델명/규격', '제조사', 'UL', 'CE', 'KC', '기타', '단위', '단가']

    header_row_index = 1  # pandas header=0 과 동일(1번째 줄이 헤더)
    header_cells = [cell.value for cell in ws[header_row_index]]
    header = [str(v).strip() if v is not None else "" for v in header_cells]
    header_map = {name: idx for idx, name in enumerate(header)}

    if not all(col in header_map for col in required_cols):
        return [], 0

    for row in ws.iter_rows(min_row=header_row_index + 1, values_only=True):
        # clean_value를 적용하지 않은 원본 모델명/규격 값 (비어있는지, '-'인지 확인용)
        raw_part_name = str(row[header_map['모델명/규격']] if header_map['모델명/규격'] < len(row) else "").strip()
        
        # ⚠️ 필터링 조건: 원본 모델명/규격이 '-'인 경우만 건너뜁니다.
        if raw_part_name == '-': 
            skipped_count += 1
            continue

        try:
            # 모든 필드에 clean_value 적용 (빈 값은 ""가 됨)
            part_name = clean_value(row[header_map['모델명/규격']] if header_map['모델명/규격'] < len(row) else None)
            maker_name = clean_maker_name(row[header_map['제조사']] if header_map['제조사'] < len(row) else None)
            major_category = clean_value(row[header_map['Unit']] if header_map['Unit'] < len(row) else None)
            minor_category = clean_value(row[header_map['품목']] if header_map['품목'] < len(row) else None)
            
            ul_status = clean_value(row[header_map['UL']] if header_map['UL'] < len(row) else None) == 'O'
            ce_status = clean_value(row[header_map['CE']] if header_map['CE'] < len(row) else None) == 'O'
            kc_status = clean_value(row[header_map['KC']] if header_map['KC'] < len(row) else None) == 'O'
            
            price_str = clean_value(row[header_map['단가']] if header_map['단가'] < len(row) else None).replace(',', '').strip()
            # price_str이 "" (빈 문자열)이 되는 경우를 대비하여 isdigit() 검사 전에 strip()
            solo_price = int(price_str.strip()) if price_str.strip().isdigit() else 0
            
            part_json = {
                "maker_name": maker_name,
                "major_category": major_category,
                "minor_category": minor_category,
                "name": part_name,
                "unit": clean_value(row[header_map['단위']] if header_map['단위'] < len(row) else "ea") or "ea",
                "solo_price": solo_price,
                "display_order": len(data_list),
                "ul": ul_status,
                "ce": ce_status,
                "kc": kc_status,
                "certification_etc": clean_value(row[header_map['기타']] if header_map['기타'] < len(row) else None),
            }
            data_list.append(part_json)

        except Exception as e:
            skipped_count += 1
            pass

    return data_list, skipped_count

def post_json(url: str, payload: dict) -> tuple[int, str]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.getcode(), body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return e.code, body

def post_parts_to_api(data_list, api_url):
    """변환된 부품 데이터 리스트를 API에 POST 요청으로 전송합니다. (이전과 동일)"""
    print(f"\n--- 부품 API 전송 시작 ({len(data_list)}개 부품) ---")
    
    success_count = 0
    failure_count = 0
    
    for part_data in data_list:
        try:
            status_code, body = post_json(api_url, part_data)

            if 200 <= status_code < 300:
                success_count += 1
            else:
                failure_count += 1
                response_text = body
                if len(response_text) > 100:
                    response_text = response_text[:100] + "..."
                # 부품명에 공백이 있을 수 있으므로 repr()로 출력하여 명확하게 합니다.
                print(f"[FAIL] 실패: {repr(part_data['name'])} (Status: {status_code}, 응답: {response_text})")
                
        except urllib.error.URLError as e:
            failure_count += 1
            print(f"[ERROR] 연결 오류: {repr(part_data['name'])} 전송 실패. ({e})")

    print(f"\n--- API 전송 완료 ---")
    print(f"[OK] 성공적으로 등록된 부품: {success_count}개")
    print(f"[FAIL] 등록 실패/오류 부품: {failure_count}개")


if __name__ == "__main__":
    # ⚠️ 중요: register_makers.py를 먼저 실행하여 빈 제조사("")가 등록되었는지 확인하세요.
    all_parts_data, skipped_count = get_parts_data_from_excel(EXCEL_FILE_PATH, PARTS_SHEET_NAME)

    if all_parts_data:
        total_converted = len(all_parts_data)
        print(f"총 {total_converted}개의 부품 데이터가 JSON 형식으로 변환되었습니다.")
        # 제외된 행은 '-'인 경우만 남습니다.
        print(f"[INFO] {skipped_count}개의 행이 '부품명'이 '-'여서 제외되었습니다. (총 변환 시도: {total_converted + skipped_count}개)")
        post_parts_to_api(all_parts_data, API_URL)
    else:
        print("[ERROR] 변환된 데이터가 없어 API 전송을 시작하지 않습니다.")
