"""
중복 T000 부품 정리 스크립트
- minor_category 기준으로 가장 낮은 ID만 남기고 나머지 삭제
"""
import urllib.request
import json

API_URL = "http://localhost:8005/api/v1/parts"

def get_all_t000_parts():
    """T000 부품 전체 조회"""
    url = f"{API_URL}?limit=1000"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())

    items = data.get("items", [])
    return [i for i in items if i.get("maker_id") == "T000"]

def find_duplicates(t000_items):
    """minor_category 기준 중복 찾기"""
    from collections import defaultdict

    by_minor = defaultdict(list)
    for item in t000_items:
        key = item.get("minor_category", "")
        by_minor[key].append(item)

    to_delete = []
    to_keep = []

    for minor, group in by_minor.items():
        sorted_group = sorted(group, key=lambda x: x["id"])
        to_keep.append(sorted_group[0])
        to_delete.extend(sorted_group[1:])

    return to_keep, to_delete

def delete_part(part_id, maker_id="T000"):
    """부품 삭제 - API: DELETE /{parts_id}/{maker_id}"""
    url = f"{API_URL}/{part_id}/{maker_id}"
    req = urllib.request.Request(url, method="DELETE")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status == 200 or resp.status == 204
    except Exception as e:
        print(f"  Error deleting {part_id}: {e}")
        return False

def main():
    print("1. T000 부품 조회 중...")
    t000_items = get_all_t000_parts()
    print(f"   총 {len(t000_items)}개 T000 부품 발견")

    print("\n2. 중복 분석 중...")
    to_keep, to_delete = find_duplicates(t000_items)
    print(f"   유지: {len(to_keep)}개")
    print(f"   삭제 대상: {len(to_delete)}개")

    if not to_delete:
        print("\n삭제할 중복 항목이 없습니다.")
        return

    print("\n3. 중복 항목 삭제 중...")
    deleted = 0
    failed = 0
    for i, item in enumerate(to_delete):
        part_id = item["id"]
        minor = item.get("minor_category", "")[:20]
        if delete_part(part_id):
            deleted += 1
            if (i + 1) % 50 == 0:
                print(f"   진행: {i+1}/{len(to_delete)} 삭제됨")
        else:
            failed += 1

    print(f"\n완료!")
    print(f"   삭제 성공: {deleted}개")
    print(f"   삭제 실패: {failed}개")
    print(f"   남은 T000 부품: {len(to_keep)}개")

if __name__ == "__main__":
    main()
