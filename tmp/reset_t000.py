"""
T000 부품 전체 삭제 및 재등록
"""
import urllib.request
import json

API_URL = "http://localhost:8005/api/v1/parts"

def get_all_t000():
    url = f"{API_URL}?limit=1000"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
    return [i for i in data.get("items", []) if i.get("maker_id") == "T000"]

def delete_part(part_id):
    url = f"{API_URL}/{part_id}/T000"
    req = urllib.request.Request(url, method="DELETE")
    try:
        with urllib.request.urlopen(req) as resp:
            return True
    except:
        return False

def main():
    print("=== T000 부품 전체 삭제 ===")

    t000_items = get_all_t000()
    print(f"삭제 대상: {len(t000_items)}개")

    deleted = 0
    for item in t000_items:
        if delete_part(item["id"]):
            deleted += 1

    print(f"삭제 완료: {deleted}개")

    # 확인
    remaining = get_all_t000()
    print(f"남은 T000: {len(remaining)}개")

if __name__ == "__main__":
    main()
