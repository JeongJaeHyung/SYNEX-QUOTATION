import sys
import os
import threading
import webview
import uvicorn
from pathlib import Path

# 1. 경로 설정
base_dir = Path(__file__).resolve().parent
sys.path.insert(0, os.path.join(base_dir, "app"))

from main import app

# 2. 서버 실행 함수 (debug/reload 인자 제거)
def run_server():
    # pywebview와 함께 쓸 때는 reload를 사용할 수 없습니다.
    uvicorn.run(app, host="127.0.0.1", port=8001)

if __name__ == "__main__":
    t = threading.Thread(target=run_server, daemon=True)
    t.start()

    webview.create_window("JLT 견적 관리 시스템", "http://127.0.0.1:8001")
    # gui='gtk'를 명시적으로 추가
    webview.start(gui='qt')

    # 4. 앱 창 생성 및 실행
    webview.create_window("JLT 견적 관리 시스템", "http://127.0.0.1:8001")
    webview.start()