# 프론트엔드 코드 분리 및 리팩토링 계획

현재 `Server/app/frontend/template/*.html` 파일에 HTML, CSS, JavaScript가 모두 혼재되어 있어(Monolithic), 유지보수와 협업이 어려운 상태입니다. 이를 표준적인 정적 자원 구조로 분리하여 코드의 가독성과 재사용성을 높이는 계획입니다.

## 1. 목표 디렉토리 구조 (Target Structure)

현재 구조를 아래와 같이 변경합니다. 페이지별로 전용 CSS와 JS 파일을 생성하여 관리합니다.

```text
Server/app/frontend/
├── template/                  # HTML (구조)
│   ├── base.html              (레이아웃)
│   ├── machine_create.html    (HTML 태그만 남김)
│   ├── parts_list_direct.html (HTML 태그만 남김)
│   └── ...
│
└── static/
    ├── css/                   # Stylesheets
    │   ├── common.css         (공통 스타일: 버튼, 레이아웃 등)
    │   ├── page/              # 페이지별 전용 스타일
    │   │   ├── machine_create.css
    │   │   └── parts_list_direct.css
    │   └── ...
    │
    └── js/                    # Scripts
        ├── common.js          (공통 유틸리티: 포맷팅, 모달 등)
        ├── api.js             (API 통신 모듈: fetch wrapper)
        ├── page/              # 페이지별 전용 로직
        │   ├── machine_create.js
        │   └── parts_list_direct.js
        └── ...
```

## 2. 상세 실행 단계 (Action Plan)

### 1단계: 디렉토리 준비
*   `Server/app/frontend/static/css/page/` 디렉토리 생성
*   `Server/app/frontend/static/js/page/` 디렉토리 생성

### 2단계: CSS 분리 (스타일)
1.  HTML 파일 내의 `<style>` 태그 내용을 잘라냅니다.
2.  `static/css/page/[페이지명].css` 파일을 생성하여 붙여넣습니다.
3.  HTML 파일 `<head>` 영역(또는 `{% block head %}`)에 CSS 파일을 링크합니다.
    ```html
    <link rel="stylesheet" href="{{ url_for('static', path='/css/page/parts_list_direct.css') }}">
    ```

### 3단계: JavaScript 분리 (로직)
1.  HTML 파일 내의 `<script>` 태그 내용을 잘라냅니다.
2.  `static/js/page/[페이지명].js` 파일을 생성하여 붙여넣습니다.
3.  HTML 파일 하단(`{% block scripts %}`)에 JS 파일을 스크립트로 로드합니다.
    ```html
    <script src="{{ url_for('static', path='/js/page/parts_list_direct.js') }}"></script>
    ```

### 🚨 4단계: Jinja2 템플릿 변수 처리 (중요)
JS 파일로 코드를 옮기면 `{{ variable }}` 같은 서버 템플릿 문법이 작동하지 않습니다. 따라서 **데이터 주입(Injection)** 방식을 변경해야 합니다.

*   **변경 전 (HTML 내 JS):**
    ```javascript
    const machineId = "{{ machine_id }}"; // 바로 사용 가능
    ```
*   **변경 후 (분리된 JS):**
    1.  **HTML 파일** 상단에 전역 변수로 데이터 선언
        ```html
        <script>
            // 서버 데이터를 전역 상수로 주입
            window.PAGE_DATA = {
                machineId: "{{ machine_id }}",
                mode: "{{ mode }}",
                initialData: {{ data | tojson | safe }}
            };
        </script>
        <script src="/static/js/page/machine_create.js"></script>
        ```
    2.  **JS 파일**에서 해당 변수 사용
        ```javascript
        const machineId = window.PAGE_DATA.machineId;
        ```

### 5단계: 공통 요소 추출 (Refactoring)
*   **CSS**: `btn`, `input`, `table` 등 여러 페이지에 반복되는 스타일을 `common.css`로 이동합니다.
*   **JS**: `formatPrice()`, `fetchAPI()` 등 범용 함수를 `common.js`로 이동하여 중복 코드를 제거합니다.

## 3. 기대 효과
1.  **가독성**: 2,000줄 넘는 코드가 HTML(300줄), CSS(500줄), JS(1200줄) 등으로 나뉘어 관리가 편해집니다.
2.  **캐싱 성능**: CSS/JS 파일이 브라우저에 캐시되어 페이지 로딩 속도가 개선됩니다.
3.  **협업 효율**: 퍼블리셔(CSS), 프론트엔드(JS), 백엔드(HTML/Data) 작업자가 동시에 파일을 수정해도 충돌이 줄어듭니다.
