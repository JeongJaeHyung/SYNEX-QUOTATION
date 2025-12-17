# SYNEX+QUOTATION/Server/app/desktop_main.py
# PyWebView 데스크톱 앱 진입점

import os
import sys
import threading
import time

# SQLite 모드 강제 설정 (다른 import 전에 설정해야 함)
os.environ["DB_MODE"] = "sqlite"


def get_resource_path(relative_path: str) -> str:
    """PyInstaller frozen 앱 또는 개발 환경의 리소스 경로 반환"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def initialize_database():
    """데이터베이스 초기화 (테이블 생성)"""
    from database import engine, Base, init_db

    # 모든 모델 import (테이블 메타데이터 등록)
    from models import (
        Maker, Resources, Certification, Machine, MachineResources,
        Account, Role, Permission, role_permission,
        General, Quotation, QuotationResources,
        Detailed, DetailedResources,
        PriceCompare, PriceCompareResources, PriceCompareMachine
    )

    # 테이블 생성
    init_db()
    print("[Desktop] 데이터베이스 초기화 완료")


def start_server(host: str = "127.0.0.1", port: int = 8765):
    """FastAPI 서버를 백그라운드에서 실행"""
    import uvicorn
    from main import app

    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="warning",
        access_log=False
    )
    server = uvicorn.Server(config)

    print(f"[Desktop] 서버 시작: http://{host}:{port}")
    server.run()


def wait_for_server(host: str, port: int, timeout: int = 10) -> bool:
    """서버가 시작될 때까지 대기"""
    import socket

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except (socket.error, socket.timeout):
            time.sleep(0.1)
    return False


def main():
    """메인 함수: PyWebView 윈도우 생성 및 서버 시작"""
    import webview

    HOST = "127.0.0.1"
    PORT = 8765

    print("[Desktop] SYNEX+ 견적 시스템 시작 중...")

    # 1. 데이터베이스 초기화
    initialize_database()

    # 2. 서버를 백그라운드 스레드에서 시작
    server_thread = threading.Thread(
        target=start_server,
        args=(HOST, PORT),
        daemon=True
    )
    server_thread.start()

    # 3. 서버가 시작될 때까지 대기
    if not wait_for_server(HOST, PORT):
        print("[Desktop] 오류: 서버 시작 실패")
        sys.exit(1)

    print("[Desktop] 서버 준비 완료")

    # 4. PyWebView 윈도우 생성
    window = webview.create_window(
        title="SYNEX+ 견적 시스템",
        url=f"http://{HOST}:{PORT}",
        width=1400,
        height=900,
        min_size=(1200, 700),
        resizable=True,
        text_select=True,
        confirm_close=True
    )

    # 5. PyWebView 시작 (이 함수는 윈도우가 닫힐 때까지 블로킹됨)
    webview.start(debug=False)

    print("[Desktop] 앱 종료")


if __name__ == "__main__":
    main()
