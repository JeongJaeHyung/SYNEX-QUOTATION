"""
DB 전체 초기화 스크립트
FK 제약조건 순서대로 삭제
"""
import urllib.request
import json

BASE_URL = "http://localhost:8005/api/v1"

def delete_all(endpoint, id_field="id", extra_path=""):
    """해당 엔드포인트의 모든 항목 삭제"""
    url = f"{BASE_URL}/{endpoint}?limit=1000"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"  조회 실패: {e}")
        return 0

    items = data.get("items", [])
    deleted = 0

    for item in items:
        item_id = item.get(id_field)
        if not item_id:
            continue

        if extra_path:
            # parts의 경우 /{id}/{maker_id} 형식
            maker_id = item.get("maker_id", "")
            del_url = f"{BASE_URL}/{endpoint}/{item_id}/{maker_id}"
        else:
            del_url = f"{BASE_URL}/{endpoint}/{item_id}"

        req = urllib.request.Request(del_url, method="DELETE")
        try:
            with urllib.request.urlopen(req) as resp:
                deleted += 1
        except Exception as e:
            pass  # 에러 무시

    return deleted

def main():
    print("=== DB 전체 초기화 ===\n")

    # 1. Machine (견적서) 삭제 - machine_resources도 CASCADE로 삭제됨
    print("1. 견적서(Machine) 삭제...")
    url = f"{BASE_URL}/quotation/machine/?limit=100"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())

    machines = data.get("items", [])
    deleted = 0
    for m in machines:
        del_url = f"{BASE_URL}/quotation/machine/{m['id']}"
        req = urllib.request.Request(del_url, method="DELETE")
        try:
            with urllib.request.urlopen(req) as resp:
                deleted += 1
        except Exception as e:
            print(f"  삭제 실패 {m['id'][:8]}: {e}")
    print(f"   {deleted}개 삭제\n")

    # 2. Parts (Resources) 삭제
    print("2. 부품(Parts) 삭제...")
    url = f"{BASE_URL}/parts?limit=1000"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())

    parts = data.get("items", [])
    deleted = 0
    for p in parts:
        del_url = f"{BASE_URL}/parts/{p['id']}/{p['maker_id']}"
        req = urllib.request.Request(del_url, method="DELETE")
        try:
            with urllib.request.urlopen(req) as resp:
                deleted += 1
        except:
            pass
    print(f"   {deleted}개 삭제\n")

    # 3. Maker 삭제
    print("3. 제조사(Maker) 삭제...")
    url = f"{BASE_URL}/maker?limit=1000"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())

    makers = data.get("items", [])
    deleted = 0
    for m in makers:
        del_url = f"{BASE_URL}/maker/{m['id']}"
        req = urllib.request.Request(del_url, method="DELETE")
        try:
            with urllib.request.urlopen(req) as resp:
                deleted += 1
        except:
            pass
    print(f"   {deleted}개 삭제\n")

    print("=== 초기화 완료 ===")

if __name__ == "__main__":
    main()
