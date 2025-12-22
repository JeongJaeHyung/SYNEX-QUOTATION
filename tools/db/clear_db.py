import sqlite3
import os

# 로그에 찍힌 경로 사용
DB_PATH = 'database/jlt_quotation.db'

def clear_resources():
    if not os.path.exists(DB_PATH):
        print(f"❌ DB 파일을 찾을 수 없어: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        # 외래 키 제약 조건 잠시 끄기 (편리한 삭제를 위해)
        cur.execute("PRAGMA foreign_keys = OFF;")

        # 참조하는 테이블들부터 데이터 삭제
        tables_to_clear = [
            'machine_resources', 
            'quotation_resources', 
            'detailed_resources', 
            'price_compare_resources',
            'resources'
        ]

        for table in tables_to_clear:
            cur.execute(f"DELETE FROM {table};")
            print(f"🗑️ {table} 테이블 데이터 삭제 완료.")

        conn.commit()
        print("\n✨ 모든 데이터가 성공적으로 초기화되었습니다.")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        conn.rollback()
    finally:
        cur.execute("PRAGMA foreign_keys = ON;")
        conn.close()

if __name__ == "__main__":
    clear_resources()