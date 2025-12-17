# SYNEX+QUOTATION/Server/app/utils/path_utils.py
# PyInstaller 호환 경로 유틸리티

import os
import sys


def get_resource_path(relative_path: str) -> str:
    """
    PyInstaller로 빌드된 exe에서도 정적 파일 경로를 올바르게 찾습니다.

    Args:
        relative_path: app 폴더 기준 상대 경로 (예: "frontend/static")

    Returns:
        절대 경로 문자열
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 exe 실행 시
        base_path = sys._MEIPASS
    else:
        # 개발 환경
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
