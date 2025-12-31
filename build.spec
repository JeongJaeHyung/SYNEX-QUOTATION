# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

block_cipher = None

# 프로젝트 경로
PROJECT_DIR = Path(SPECPATH)

# 데이터 파일 수집
datas = [
    # frontend 폴더 전체
    (str(PROJECT_DIR / 'frontend'), 'frontend'),
    # backend 폴더 전체
    (str(PROJECT_DIR / 'backend'), 'backend'),
    # database 폴더
    (str(PROJECT_DIR / 'database'), 'database'),
]

# hidden imports (동적으로 import되는 모듈들)
hiddenimports = [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.lifespan.off',
    'jinja2',
    'sqlalchemy',
    'sqlalchemy.sql.default_comparator',
    'sqlalchemy.dialects.sqlite',
    'pydantic',
    'pydantic_settings',
    'webview',
    'webview.platforms.winforms',
    'clr_loader',
    'pythonnet',
    'playwright',
    'playwright.async_api',
    'playwright.sync_api',
    'greenlet',
]

a = Analysis(
    ['run.py'],
    pathex=[str(PROJECT_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='JLT_Quotation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI 앱이므로 콘솔 숨김
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 아이콘 파일 있으면 여기 추가: 'assets/icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='JLT_Quotation',
)
