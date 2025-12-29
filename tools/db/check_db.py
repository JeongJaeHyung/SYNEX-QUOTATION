import os
import sqlite3

DB_PATH = "database/jlt_quotation.db"


def check():
    if not os.path.exists(DB_PATH):
        print(f"❌ DB 파일을 찾을 수 없어: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        # 1. 테이블 목록 조회
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cur.fetchall()]
        print(f"📊 생성된 테이블: {', '.join(tables)}")

        # 2. 제조사 수 확인
        if "maker" in tables:
            cur.execute("SELECT COUNT(*) FROM maker")
            print(f"🏭 제조사(Maker) 수: {cur.fetchone()[0]}")

        # 3. 부품 수 확인
        if "resources" in tables:
            cur.execute("SELECT COUNT(*) FROM resources")
            print(f"📦 부품(Resources) 수: {cur.fetchone()[0]}")

            # 데이터 샘플 확인 (복합 키 구조 확인용)
            print("\n🔍 부품 데이터 샘플 (최근 3개):")
            cur.execute("SELECT id, maker_id, name, solo_price FROM resources LIMIT 3")
            for row in cur.fetchall():
                print(
                    f"   - ID: {row[0]} | Maker: {row[1]} | Name: {row[2]} | Price: {row[3]}"
                )

    except Exception as e:
        print(f"❌ 조회 중 에러 발생: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    check()
