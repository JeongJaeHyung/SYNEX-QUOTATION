# SYNEX+ 견적 시스템 - 빌드 가이드

데스크톱 앱 빌드 및 배포 가이드입니다.

---

## 목차

1. [개발 환경 설정](#1-개발-환경-설정)
2. [데이터베이스 생성](#2-데이터베이스-생성)
3. [초기 데이터 주입](#3-초기-데이터-주입)
4. [데스크톱 앱 테스트](#4-데스크톱-앱-테스트)
5. [exe 패키징 (PyInstaller)](#5-exe-패키징-pyinstaller)
6. [설치 파일 생성 (Inno Setup)](#6-설치-파일-생성-inno-setup)
7. [PostgreSQL → SQLite 마이그레이션](#7-postgresql--sqlite-마이그레이션)

---

## 1. 개발 환경 설정

### 필수 설치

```bash
# Python 패키지 설치
cd Server
pip install -r requirements-desktop.txt
```

### requirements-desktop.txt 주요 패키지

| 패키지 | 용도 |
|--------|------|
| `pywebview` | 데스크톱 GUI 창 |
| `pyinstaller` | exe 빌드 |
| `uvicorn` | FastAPI 서버 |
| `sqlalchemy` | ORM |

---

## 2. 데이터베이스 생성

### 방법 A: SQLite (데스크톱용)

SQLite는 별도 서버 없이 파일 기반으로 동작합니다.

```bash
cd Server/app

# 환경변수 설정 (Windows CMD)
set DB_MODE=sqlite

# 환경변수 설정 (PowerShell)
$env:DB_MODE="sqlite"

# 환경변수 설정 (Git Bash)
export DB_MODE=sqlite

# Python에서 테이블 생성
python -c "from database import engine, Base; from models import *; Base.metadata.create_all(bind=engine)"
```

생성 위치: `Server/app/data/synex_quotation.db`

### 방법 B: PostgreSQL (웹 서버용)

```bash
# Docker로 PostgreSQL 실행
cd DataBase
docker-compose up -d

# 환경변수 설정
set DB_MODE=postgresql
set DB_USER=postgres
set DB_PASSWORD=1234
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=synex_quotation_db

# 테이블 생성
cd ../Server/app
python -c "from database import engine, Base; from models import *; Base.metadata.create_all(bind=engine)"
```

---

## 3. 초기 데이터 주입

### 방법 A: 엑셀 파일에서 로드

엑셀 파일 구조:
- `maker` 시트: 제조사 목록 (이름, 코드)
- `parts` 시트: 부품/자재 목록
- 기타 시트: 장비 템플릿

```bash
cd Server/app

# SQLite 모드
set DB_MODE=sqlite
python tools/load_excel_data.py ../tmp/data.xlsx

# PostgreSQL 모드
set DB_MODE=postgresql
set DB_USER=postgres
set DB_PASSWORD=1234
python tools/load_excel_data.py ../tmp/data.xlsx
```

### 방법 B: 초기 데이터 스크립트

```bash
cd Server/app

# 기본 데이터 생성 (계정, 권한 등)
python tools/init_data.py
```

### 엑셀 파일 형식

**maker 시트:**
| 회사명 | 회사코드 |
|--------|----------|
| LS ELECTRIC | LS |
| SIEMENS | SM |

**parts 시트:**
| Unit | 품목 | 모델명/규격 | 제조사 | UL | CE | KC | 기타 | 단위 | 단가 |
|------|------|-------------|--------|----|----|----|----|------|------|

---

## 4. 데스크톱 앱 테스트

개발 중 PyWebView 앱을 테스트하는 방법입니다.

```bash
cd Server/app

# SQLite 모드로 실행
set DB_MODE=sqlite
python desktop_main.py
```

브라우저 창이 열리면서 앱이 실행됩니다 (1400x900).

### desktop_main.py 주요 설정

```python
# 포트 설정
HOST = "127.0.0.1"
PORT = 8765

# 창 크기
window = webview.create_window(
    title="SYNEX+ 견적 시스템",
    url=f"http://{HOST}:{PORT}",
    width=1400,
    height=900
)
```

---

## 5. exe 패키징 (PyInstaller)

### 빌드 명령어

```bash
cd Server

# spec 파일로 빌드
pyinstaller synex_quotation.spec
```

결과: `Server/dist/SYNEX_Quotation.exe`

### spec 파일 구조 설명

```python
# synex_quotation.spec

# 1. 포함할 데이터 파일 (정적 파일, 템플릿, 이미지)
datas = [
    ('app/frontend/static', 'frontend/static'),
    ('app/frontend/template', 'frontend/template'),
    ('app/frontend/element', 'frontend/element'),
    ('app/frontend/assets', 'frontend/assets'),  # 비디오 포함
]

# 2. 숨겨진 import (자동 감지 안 되는 모듈)
hiddenimports = [
    'uvicorn', 'uvicorn.logging', ...
    'sqlalchemy.dialects.sqlite', ...
    'webview', ...
]

# 3. 제외할 모듈 (불필요한 대용량 모듈)
excludes = [
    'psycopg2',  # PostgreSQL 드라이버 (SQLite만 사용)
    'tkinter', 'numpy', 'pandas', ...
]

# 4. EXE 설정
exe = EXE(
    ...
    name='SYNEX_Quotation',
    console=False,  # GUI 앱 (콘솔 창 숨김)
)
```

### 자주 발생하는 오류

| 오류 | 원인 | 해결 |
|------|------|------|
| `ModuleNotFoundError: jaraco` | pkg_resources 의존성 | hiddenimports에 추가 |
| `Directory does not exist` | 정적 파일 경로 | `get_resource_path()` 사용 |
| `No module named 'xyz'` | 숨겨진 import | hiddenimports에 추가 |

### 경로 해상도 (PyInstaller 호환)

exe로 빌드하면 경로가 달라집니다. `utils/path_utils.py` 사용:

```python
from utils.path_utils import get_resource_path

# 개발 환경: Server/app/frontend/static
# exe 환경: _MEIPASS/frontend/static
STATIC_DIR = get_resource_path("frontend/static")
```

---

## 6. 설치 파일 생성 (Inno Setup)

### Inno Setup 설치

```bash
# winget으로 설치
winget install -e --id JRSoftware.InnoSetup
```

또는 https://jrsoftware.org/isdl.php 에서 다운로드

### 설치 파일 빌드

```bash
# 명령줄에서 컴파일
"C:\Users\{사용자}\AppData\Local\Programs\Inno Setup 6\ISCC.exe" Server\installer.iss

# 또는 GUI로 열기
# Inno Setup Compiler 실행 → installer.iss 열기 → Build → Compile
```

결과: `Server/installer_output/SYNEX_Quotation_Setup.exe`

### installer.iss 구조 설명

```ini
; 1. 앱 정보
#define MyAppName "SYNEX+ 견적 시스템"
#define MyAppVersion "1.0.0"

[Setup]
AppId={{고유-GUID}}
AppName={#MyAppName}
DefaultDirName={autopf}\SYNEX_Quotation  ; Program Files에 설치
OutputBaseFilename=SYNEX_Quotation_Setup

; 2. 포함할 파일
[Files]
Source: "dist\SYNEX_Quotation.exe"; DestDir: "{app}"
Source: "dist\data\*"; DestDir: "{app}\data"

; 3. 바로가기
[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"  ; 시작 메뉴
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"  ; 바탕화면

; 4. 설치 후 실행
[Run]
Filename: "{app}\{#MyAppExeName}"; Flags: postinstall
```

### 버전 업데이트 시

1. `installer.iss`에서 `MyAppVersion` 수정
2. `OutputBaseFilename`에 버전 추가 (선택)
3. 다시 컴파일

---

## 7. PostgreSQL → SQLite 마이그레이션

웹 서버의 PostgreSQL 데이터를 데스크톱용 SQLite로 옮기는 방법입니다.

```bash
cd Server/app

# PostgreSQL 환경변수 설정
set DB_USER=postgres
set DB_PASSWORD=1234
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=synex_quotation_db

# 마이그레이션 실행
python tools/migrate_to_sqlite.py
```

결과: `Server/app/data/synex_quotation.db`

---

## 전체 빌드 플로우

```
1. 데이터 준비
   └─ 엑셀 파일 또는 PostgreSQL 데이터

2. SQLite DB 생성
   └─ load_excel_data.py 또는 migrate_to_sqlite.py

3. 데스크톱 앱 테스트
   └─ python desktop_main.py

4. exe 빌드
   └─ pyinstaller synex_quotation.spec
   └─ dist/SYNEX_Quotation.exe 생성

5. DB 파일 복사
   └─ app/data/synex_quotation.db → dist/data/

6. 설치 파일 생성
   └─ ISCC.exe installer.iss
   └─ installer_output/SYNEX_Quotation_Setup.exe 생성

7. 배포
   └─ Setup.exe 파일 배포
```

---

## 파일 구조

```
Server/
├── app/
│   ├── data/
│   │   └── synex_quotation.db      # SQLite DB
│   ├── desktop_main.py             # PyWebView 진입점
│   ├── database.py                 # 듀얼 모드 DB 설정
│   ├── utils/
│   │   └── path_utils.py           # PyInstaller 경로 유틸
│   └── tools/
│       ├── load_excel_data.py      # 엑셀 → DB
│       ├── migrate_to_sqlite.py    # PostgreSQL → SQLite
│       └── init_data.py            # 초기 데이터
├── dist/
│   ├── SYNEX_Quotation.exe         # 빌드된 exe
│   └── data/
│       └── synex_quotation.db      # 배포용 DB
├── installer_output/
│   └── SYNEX_Quotation_Setup.exe   # 설치 파일
├── synex_quotation.spec            # PyInstaller 설정
├── installer.iss                   # Inno Setup 스크립트
└── requirements-desktop.txt        # 데스크톱 의존성
```
