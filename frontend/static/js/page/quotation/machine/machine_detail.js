// app/frontend/static/js/page/machine_detail.js
//
// 장비 견적서 상세 페이지(machine_detail.html)의 클라이언트 측 JavaScript 로직을 정의합니다.
// - URL에서 견적서 ID를 추출하여 해당 견적서의 상세 정보를 API로 로드합니다.
// - 로드된 데이터를 화면에 렌더링하고, 관련 버튼(목록, 수정, PDF 다운로드)의 동작을 정의합니다.
//

// --- 전역 변수 선언 및 초기화 ---
// URL 경로에서 machineId를 추출합니다. (예: /service/quotation/machine/123e4567-e89b-12d3-a456-426614174000)
const pathParts = window.location.pathname.split('/');
const machineId = pathParts[pathParts.length - 1]; // 배열의 마지막 요소가 ID입니다.

// --- 이벤트 리스너: 페이지 로드 시 ---
// DOMContentLoaded 이벤트는 HTML 문서의 파싱이 완료되었을 때 발생합니다.
document.addEventListener('DOMContentLoaded', function() {
    loadMachineDetail(); // 페이지 로드 후 견적서 상세 정보 로드 함수 호출
});

// --- 비동기 함수: 장비 견적서 상세 정보 로드 ---
async function loadMachineDetail() {
    // HTML 요소들을 참조합니다.
    const loading = document.getElementById('loading');         // 로딩 인디케이터
    const errorMessage = document.getElementById('errorMessage'); // 에러 메시지 영역
    const detailContainer = document.getElementById('detailContainer'); // 상세 정보 컨테이너
    
    // 로딩 인디케이터를 표시하고 상세 정보 컨테이너와 에러 메시지는 숨깁니다.
    if (loading) loading.style.display = 'block';
    if (errorMessage) errorMessage.style.display = 'none';
    if (detailContainer) detailContainer.style.display = 'none';

    try {
        // 백엔드 API로부터 특정 machineId에 해당하는 견적서 상세 정보를 요청합니다.
        // include_schema=true를 통해 데이터 스키마도 함께 받아 테이블 렌더링에 활용합니다.
        const response = await fetch(`/api/v1/quotation/machine/${machineId}?include_schema=true`);
        
        // HTTP 응답이 성공적이지 않으면 에러를 발생시킵니다.
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json(); // 응답 본문을 JSON으로 파싱합니다.
        console.log('Machine Detail:', data); // 개발자 콘솔에 상세 데이터를 로깅합니다.
        
        // 로드된 데이터를 사용하여 화면에 상세 정보를 렌더링합니다.
        renderMachineDetail(data);
        
        // 로딩 인디케이터를 숨기고 상세 정보 컨테이너를 표시합니다.
        if (loading) loading.style.display = 'none';
        if (detailContainer) detailContainer.style.display = 'block';
        
    } catch (error) {
        // API 호출 실패 또는 데이터 처리 중 에러 발생 시
        console.error('Error:', error); // 에러를 콘솔에 로깅합니다.
        
        // 로딩 인디케이터를 숨기고 에러 메시지 컨테이너를 표시합니다.
        if (loading) loading.style.display = 'none';
        if (errorMessage) errorMessage.style.display = 'block';
        // 에러 상세 내용을 화면에 표시합니다.
        const errorDetailEl = document.getElementById('errorDetail');
        if (errorDetailEl) errorDetailEl.textContent = error.message;
    }
}

// --- 함수: 견적서 상세 정보 렌더링 ---
function renderMachineDetail(data) {
    // 견적서의 기본 정보를 HTML 요소에 반영합니다.
    if (document.getElementById('machineName')) document.getElementById('machineName').textContent = data.name || '-';
    if (document.getElementById('machineId')) document.getElementById('machineId').textContent = data.id || '-';
    if (document.getElementById('creator')) document.getElementById('creator').textContent = data.creator || '-';
    if (document.getElementById('createdAt')) document.getElementById('createdAt').textContent = formatDateTime(data.created_at);
    if (document.getElementById('updatedAt')) document.getElementById('updatedAt').textContent = formatDateTime(data.updated_at);
    if (document.getElementById('totalPrice')) document.getElementById('totalPrice').textContent = formatCurrency(data.price || 0); // data.price는 총액 (백엔드에서 계산된 값)
    if (document.getElementById('description')) document.getElementById('description').textContent = data.description || '비고 없음';
    if (document.getElementById('resourceCount')) document.getElementById('resourceCount').textContent = data.resource_count || 0;
    
    // 구성 부품 테이블 렌더링 로직
    if (data.resources) {
        // API 응답에 스키마와 아이템이 모두 포함된 경우 (일반적인 경우)
        if (data.resources.schema && data.resources.items) {
            renderResourcesTable(data.resources.schema, data.resources.items);
        } else if (Array.isArray(data.resources)) {
            // 스키마 없이 아이템 배열만 있는 경우 (레거시 또는 간소화된 응답 처리)
            renderResourcesTableSimple(data.resources);
        }
    }
}

// --- 함수: 구성 부품 테이블 렌더링 (스키마 기반) ---
function renderResourcesTable(schema, items) {
    const container = document.getElementById('resourcesTable'); // 테이블이 삽입될 컨테이너
    
    if (!container) return; // 컨테이너가 없으면 함수 종료

    // 표시할 아이템이 없으면 '데이터 없음' 메시지 표시
    if (!items || items.length === 0) {
        container.innerHTML = '<div class="empty-state">구성 부품이 없습니다</div>';
        return;
    }
    
    // 스키마에 정의된 컬럼 비율을 이용하여 전체 너비 계산
    let totalRatio = 0;
    for (const key in schema) {
        totalRatio += schema[key].ratio || 1; // ratio가 없으면 기본값 1
    }
    
    let html = '<div class="table-container"><table class="data-table">';
    
    // 테이블 헤더 렌더링
    html += '<thead><tr>';
    for (const key in schema) {
        const col = schema[key];
        const width = ((col.ratio || 1) / totalRatio * 100).toFixed(1); // 비율에 따른 컬럼 너비 계산
        const align = col.align || (col.type === 'integer' ? 'right' : (col.type === 'boolean' ? 'center' : 'left')); // 기본 정렬
        html += `<th class="col-${align}" style="width: ${width}%">${col.title}</th>`;
    }
    html += '</tr></thead><tbody>';
    
    // 데이터 행 렌더링
    items.forEach(item => {
        html += '<tr>';
        for (const key in schema) {
            const col = schema[key];
            const value = item[key];
            const align = col.align || (col.type === 'integer' ? 'right' : (col.type === 'boolean' ? 'center' : 'left'));
            
            html += `<td class="col-${align}">`;
            html += formatValue(value, col.type, col.format); // 값 포맷팅하여 삽입
            html += '</td>';
        }
        html += '</tr>';
    });
    
    html += '</tbody></table></div>';
    container.innerHTML = html; // 생성된 HTML을 컨테이너에 삽입
}

// --- 함수: 구성 부품 테이블 렌더링 (간소화된 스키마 없음 버전) ---
function renderResourcesTableSimple(items) {
    const container = document.getElementById('resourcesTable');
    
    if (!container) return;

    if (!items || items.length === 0) {
        container.innerHTML = '<div class="empty-state">구성 부품이 없습니다</div>';
        return;
    }
    
    let html = '<div class="table-container"><table class="data-table">';
    
    // 고정된 헤더 렌더링 (스키마가 없는 경우)
    html += `<thead><tr>
        <th>품목코드</th>
        <th>제조사</th>
        <th>대분류</th>
        <th>중분류</th>
        <th>모델명</th>
        <th>단위</th>
        <th class="col-right">단가</th>
        <th class="col-center">수량</th>
        <th class="col-right">소계</th>
    </tr></thead><tbody>`;
    
    // 데이터 행 렌더링
    items.forEach(item => {
        html += `<tr>
            <td>${item.item_code || '-'}</td>
            <td>${item.maker_name || '-'}</td>
            <td>${item.category_major || '-'}</td>
            <td>${item.category_minor || '-'}</td>
            <td>${item.model_name || item.name || '-'}</td>
            <td>${item.unit || '-'}</td>
            <td class="col-right">${formatCurrency(item.solo_price || 0)}</td>
            <td class="col-center">${item.quantity || 0}</td>
            <td class="col-right">${formatCurrency(item.subtotal || 0)}</td>
        </tr>`;
    });
    
    html += '</tbody></table></div>';
    container.innerHTML = html;
}

// --- 헬퍼 함수: 값 포맷팅 ---
function formatValue(value, type, format) {
    if (value === null || value === undefined || value === '') {
        return '<span class="text-muted">-</span>'; // 값이 없으면 '-' 표시
    }
    
    switch(type) {
        case 'boolean': // 불리언 타입 (예: 인증 여부)
            return value ? 
                '<span class="badge badge-success">O</span>' : /* true면 O */
                '<span class="badge badge-default">X</span>'; /* false면 X */
        
        case 'integer': // 정수 타입
            if (format === 'currency') { // 통화 형식으로 포맷팅
                return formatCurrency(value);
            }
            return value.toLocaleString('ko-KR'); // 숫자 로케일 포맷팅
        
        case 'datetime': // 날짜/시간 타입
            return formatDateTime(value);
        
        default: // 그 외 타입은 값 그대로 반환
            return value;
    }
}

// --- 헬퍼 함수: 날짜/시간 포맷팅 ---
function formatDateTime(datetime) {
    if (!datetime) return '-';
    const date = new Date(datetime);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}. ${month}. ${day} ${hours}:${minutes}`;
}

// --- 헬퍼 함수: 통화 포맷팅 ---
function formatCurrency(value) {
    if (!value && value !== 0) return '-';
    return value.toLocaleString('ko-KR') + '원';
}

// --- 액션 버튼 관련 함수 ---

// 목록 페이지로 이동
function goToList() {
    window.location.href = '/service/quotation/machine/form'; // 견적서 목록 페이지로 이동
}

// 수정 페이지로 이동
function editMachine() {
    // alert('수정 기능은 구현 예정입니다.'); // 기능 구현 예정 알림 (예전 주석)
    window.location.href = `/service/quotation/machine/form?mode=edit&id=${machineId}`; // 수정 모드 페이지로 이동
}

// PDF 다운로드 (미구현)
function downloadPDF() {
    alert('PDF 다운로드 기능은 구현 예정입니다.'); // 기능 구현 예정 알림
    // TODO: PDF 생성 API 호출 및 파일 다운로드 로직
}