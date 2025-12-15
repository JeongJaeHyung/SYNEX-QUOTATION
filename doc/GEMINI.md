# SYNEX QUOTATION 시스템

## 프로젝트 개요
**SYNEX QUOTATION** 시스템은 장비 견적서를 관리하기 위한 풀스택 웹 애플리케이션입니다. 부품(자재), 제조사, 템플릿 데이터베이스를 활용하여 다양한 장비에 대한 견적서를 생성, 수정 및 관리할 수 있습니다. 사용자는 기존 템플릿을 기반으로 견적서를 생성하거나 처음부터 새로 작성할 수 있으며, 인건비를 관리하고 다양한 부품 카테고리를 처리할 수 있습니다.

## 기술 스택 (Tech Stack)

### 백엔드 (Backend)
*   **언어:** Python 3.12+
*   **프레임워크:** FastAPI
*   **ORM:** SQLAlchemy
*   **데이터베이스 마이그레이션:** Alembic
*   **컨테이너화:** Docker

### 프론트엔드 (Frontend)
*   **유형:** 서버 사이드 렌더링 (SSR)
*   **템플릿 엔진:** Jinja2 (FastAPI를 통해 제공)
*   **언어:** HTML5, CSS3, Vanilla JavaScript
*   **UI 라이브러리:** 커스텀 CSS (Bootstrap 스타일 유틸리티 사용)

### 데이터베이스 (Database)
*   **데이터베이스:** PostgreSQL 15
*   **드라이버:** `psycopg2-binary`

### 인프라 (Infrastructure)
*   **Docker:** 애플리케이션과 데이터베이스 컨테이너화에 사용
*   **Docker Compose:** Orchestrates the Postgres database and the backend server.

## 디렉토리 구조

*   `Server/`: 백엔드 애플리케이션 코드가 포함되어 있습니다.
    *   `app/`: 메인 애플리케이션 소스 코드입니다.
        *   `api/`: REST API 엔드포인트 (JSON 응답).
            *   `v1/`: 버전별 API 라우트 (예: `parts`, `maker`, `quotation`).
        *   `models/`: SQLAlchemy 데이터베이스 모델 (`machine.py`, `resources.py` 등).
        *   `frontend/`: 프론트엔드 자산.
            *   `template/`: HTML 템플릿 (Jinja2).
            *   `static/`: CSS, JS 및 이미지.
                *   `css/page/`: 페이지별 전용 CSS 파일.
                *   `js/page/`: 페이지별 전용 JavaScript 파일.
        *   `service/`: HTML 페이지를 제공하는 라우트 핸들러 (프론트엔드 로직).
    *   `alembic/`: 데이터베이스 마이그레이션 스크립트.
*   `DataBase/`: 데이터베이스 설정.
    *   `docker-compose.yml`: PostgreSQL 서비스 정의.
*   `tmp/`: 유틸리티 스크립트, 시드 데이터(엑셀 파일) 및 디버깅 스크립트(`register_templates.py`, `check_db_data.py` 등)를 위한 임시 디렉토리.
*   `doc/`: 프로젝트 관련 문서 (GEMINI.md, DATABASE.md, Work_Log 등).

## 설정 및 실행 (Setup and Running)

### 필수 조건
*   Docker & Docker Compose
*   Python 3.12+ (로컬 개발용)

### 1. 데이터베이스 설정
데이터베이스는 Docker 컨테이너에서 실행됩니다.
```bash
cd DataBase
docker-compose up -d
```
이 명령은 `synex-postgres-db` 컨테이너를 시작합니다.

### 2. 백엔드 서버 설정
서버는 로컬에서 직접 실행하거나 Docker를 통해 실행할 수 있습니다.

**로컬 개발:**
1.  `Server/`로 이동합니다.
2.  가상 환경을 생성합니다: `python -m venv venv`.
3.  활성화합니다: `source venv/bin/activate` (Linux/Mac) 또는 `venv\Scripts\activate` (Windows).
4.  의존성 패키지를 설치합니다: `pip install -r requirements.txt`.
5.  환경 변수(`.env` 파일)를 설정합니다.
6.  서버를 실행합니다:
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8005
    ```

**Docker:**
```bash
cd Server
docker-compose up -d --build
```

### 3. 데이터 시딩 (Data Seeding)
이 프로젝트는 `tmp/` 디렉토리의 스크립트를 사용하여 엑셀 파일(`SYNEX+QUOTATION INFO.xlsx`)에서 데이터를 DB로 로드합니다.
*   `python tmp/register_makers.py`: 제조사 등록.
*   `python tmp/register_parts.py`: 부품/자재 등록.
*   `python tmp/register_templates.py`: 장비 템플릿 등록.

## 주요 기능 및 개선 사항 (2025-12-14 기준)

### 1. 프론트엔드 코드 분리 (리팩토링)
*   **목표**: HTML, CSS, JavaScript 코드를 페이지별로 별도 파일로 분리하여 코드 가독성, 유지보수성, 재사용성 향상.
*   **상태**: 주요 페이지(`parts_list_direct.html`, `machine_create.html`, `machine_detail.html`, `machine_list_direct.html`, `login.html`, `register.html`)의 CSS와 JS가 `Server/app/frontend/static/css/page/` 및 `Server/app/frontend/static/js/page/` 디렉토리로 성공적으로 분리 완료.
*   **Jinja2 블록 상속**: `base.html`의 `{% block extra_css %}`와 `{% block extra_js %}`를 사용하여 페이지별 스타일/스크립트 연결.

### 2. Machine Quotation (장비 견적서) 기능 개선
*   **인건비(Labor Cost) 표시 로직 수정**: '템플릿 보기' 모드에서 템플릿에 포함되거나 수량이 0 이상인 인건비만 표시.
*   **'First Fill' 인건비 누락 수정**: `register_templates.py` 스크립트 개선을 통해 엑셀의 빈 이름/0원 단가 문제가 해결되고 DB 데이터가 정상화됨.
*   **'케이블 및 기타 잡자재' 수동 입력 전환**: 자동 합계 항목에서 사용자가 직접 금액을 입력할 수 있는 수동 항목으로 전환.
*   **조회 모드 플로팅 버튼 개선**: 조회(View) 모드에서 '저장/등록' 버튼 대신 '수정하기' 플로팅 버튼이 표시되도록 변경. '임시 저장' 버튼은 조회 모드에서 숨김.

### 3. Parts List (부품 목록) UI/UX 개선
*   **무한 스크롤(Infinite Scroll) 도입**: 페이지네이션 대신 `IntersectionObserver`를 활용한 무한 스크롤 방식으로 변경 (`limit` 30개).
*   **조회 모드 검색/필터 활성화**: 검색 및 카테고리 필터가 조회 모드에서도 동작하도록 활성화.
*   **동적 카테고리 필터 옵션**: 하드코딩된 카테고리 대신 실제 데이터에 존재하는 `Unit`(대분류) 목록으로 필터 옵션 동적 생성.
*   **인증 정보 표시 개선**: 인증 정보(UL, CE, KC)가 없을 때 'X' 대신 '-'로 표시.
*   **'순서' 컬럼 제거**: '템플릿 보기' 모드에서 불필요한 '순서' 컬럼 제거.

## 개발 참고 사항
*   **API vs Service:** `api/` 디렉토리는 JSON 데이터 교환을 처리하고, `service/` 디렉토리는 HTML 페이지 렌더링을 처리합니다.
*   **환경 설정:** DB 연결을 위해 `.env` 파일이 올바르게 설정되었는지 확인하세요 (로컬 스크립트 실행 시 `DB_HOST=localhost`, Docker 실행 시 `synex-postgres-db`).
*   **프론트엔드 코드 분리 유의사항**: Jinja2 템플릿 변수가 JavaScript 코드에 직접 사용될 경우, 분리된 `.js` 파일에서는 바로 접근할 수 없습니다. 이 경우 `window.PAGE_DATA = { /* ... */ }`와 같이 HTML 파일에서 전역 객체에 데이터를 주입한 후, `.js` 파일에서 `window.PAGE_DATA.변수명`으로 접근해야 합니다. (이슈 발생 시 `PLAN_FRONTEND_REFACTORING.md` 참고)
