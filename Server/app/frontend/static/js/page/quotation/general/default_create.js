let pageMode = 'create'; // create, view
let generalId = null;

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    // URL 파라미터에서 모드와 ID 가져오기
    const urlParams = new URLSearchParams(window.location.search);
    pageMode = urlParams.get('mode') || 'create';
    generalId = urlParams.get('id') || null;
    
    // 페이지 초기화
    initializePage();
});

// 페이지 초기화
function initializePage() {
    const titleElement = document.getElementById('pageTitle');
    const submitBtn = document.getElementById('submitBtn');
    const viewOnlyFields = document.getElementById('viewOnlyFields');
    const relationsSection = document.getElementById('relationsSection');
    const derivativeBtnGroup = document.getElementById('derivativeBtnGroup'); // 추가됨
    
    if (pageMode === 'create') {
        // 생성 모드
        titleElement.textContent = '견적서(일반) 생성';
        submitBtn.textContent = '등록완료';
        submitBtn.style.display = 'inline-block';
        viewOnlyFields.style.display = 'none';
        relationsSection.style.display = 'none';
        derivativeBtnGroup.style.display = 'none'; // 생성 중엔 숨김
        
    } else if (pageMode === 'view') {
        // 조회 모드 - 모든 필드 비활성화
        titleElement.textContent = '견적서(일반) 조회';
        submitBtn.style.display = 'none'; // 저장 버튼 숨김 (필요시 수정버튼으로 변경 가능)
        viewOnlyFields.style.display = 'flex';
        relationsSection.style.display = 'block';
        derivativeBtnGroup.style.display = 'flex'; // [핵심] 파생 버튼 보임
        
        // 입력 필드 모두 비활성화
        disableAllInputs();
        
        // 기존 데이터 로드
        if (generalId) {
            loadGeneralData(generalId);
            loadRelationsData(generalId);
        }
    }
}

// [추가된 함수] 내정가 비교서 만들기 페이지 이동
function createPriceCompare() {
    if (!generalId) return alert('잘못된 접근입니다.');
    // 우리가 만든 서브 페이지로 이동 (General ID 전달)
    window.location.href = `/service/quotation/general/price_compare/register?general_id=${generalId}`;
}

// 모든 입력 필드 비활성화 (View 모드)
function disableAllInputs() {
    document.getElementById('generalName').readOnly = true;
    document.getElementById('client').readOnly = true;
    document.getElementById('creator').readOnly = true;
    document.getElementById('description').readOnly = true;
}

// 기존 General 데이터 로드
async function loadGeneralData(id) {
    try {
        const response = await fetch(`/api/v1/quotation/general/${id}`);
        
        if (!response.ok) {
            throw new Error('데이터 로드 실패');
        }
        
        const data = await response.json();
        
        // 상단 정보 설정 (Response basic 구조 대응)
        const info = data.general || data; // 구조 유연하게 처리

        document.getElementById('generalName').value = info.name || '';
        document.getElementById('client').value = info.client || '';
        document.getElementById('creator').value = info.creator || '';
        document.getElementById('description').value = info.description || '';
        
        // 날짜 포맷팅
        if (info.created_at) {
            const createdDate = new Date(info.created_at);
            document.getElementById('createdAt').value = formatDateTime(createdDate);
        }
        if (info.updated_at) {
            const updatedDate = new Date(info.updated_at);
            document.getElementById('updatedAt').value = formatDateTime(updatedDate);
        }
        
    } catch (error) {
        console.error('Error:', error);
        alert('데이터를 불러오는데 실패했습니다.');
    }
}

// 연관 테이블 데이터 로드
async function loadRelationsData(id) {
    const loading = document.getElementById('relationsLoading');
    const tableContainer = document.getElementById('relationsTableContainer');
    
    loading.style.display = 'block';
    tableContainer.innerHTML = '';
    
    try {
        // API 호출
        const response = await fetch(`/api/v1/quotation/general/${id}?include_relations=true`);
        
        if (!response.ok) {
            throw new Error('연관 데이터 로드 실패');
        }
        
        const data = await response.json();
        
        // 기본 스키마 정의
        const schema = data.schema || {
            "category": { "title": "구분", "type": "string", "ratio": 1 },
            "title": { "title": "제목/비고", "type": "string", "ratio": 3 },
            "creator": { "title": "작성자", "type": "string", "ratio": 1 },
            "updated_at": { "title": "최종수정일", "type": "datetime", "format": "YYYY-MM-DD HH:mm", "ratio": 1.5 }
        };
        
        // 데이터 필드명 매핑 (API 응답 -> 테이블 표시용)
        const items = data.related_documents || data.items || [];

        // 연관 테이블 렌더링
        renderRelationsTable(schema, items);
        
    } catch (error) {
        console.error('Error:', error);
        tableContainer.innerHTML = '<div class="empty-state">연관 데이터를 불러오지 못했습니다.</div>';
    } finally {
        loading.style.display = 'none';
    }
}

// 연관 테이블 렌더링
function renderRelationsTable(schema, items) {
    const tableContainer = document.getElementById('relationsTableContainer');
    
    if (!items || items.length === 0) {
        tableContainer.innerHTML = '<div class="empty-state">연관된 견적서가 없습니다</div>';
        return;
    }
    
    let totalRatio = 0;
    for (const key in schema) {
        totalRatio += schema[key].ratio || 1;
    }
    
    let html = '<div class="table-container"><table class="data-table" id="relationsTable">';
    
    html += '<thead><tr>';
    for (const key in schema) {
        const col = schema[key];
        const width = ((col.ratio || 1) / totalRatio * 100).toFixed(1);
        html += `<th class="col-left" style="width: ${width}%">${col.title}</th>`;
    }
    html += '</tr></thead><tbody>';
    
    items.forEach((item) => {
        const relationId = item.id;
        const tableName = item.table_name;
        
        let detailUrl = '#';

        // ▼▼▼ [핵심 수정 부분] 테이블 이름에 따른 상세 페이지 매핑 ▼▼▼
        if (tableName === 'Quotation' || tableName === 'Machine' || tableName === '장비 견적서') { 
            // 장비 견적서 상세 (mode=view)
            detailUrl = `/service/quotation/machine/form?mode=view&id=${relationId}`;
        } 
        else if (tableName === 'Detailed' || tableName === '견적서(상세)') {
            // 을지 상세 (mode=view)
            detailUrl = `/service/quotation/detailed/form?mode=view&id=${relationId}`;
        } 
        else if (tableName === 'PriceCompare' || tableName === '내정가비교' || tableName === '비교 견적서') { 
            // [중요] 내정가 비교서 상세 페이지 (/detail/{id})
            detailUrl = `/service/quotation/general/price_compare/detail/${relationId}`;
        }
        // ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
        
        html += `<tr class="clickable" onclick="window.location.href='${detailUrl}'">`;
        
        for (const key in schema) {
            const col = schema[key];
            const value = item[key];
            
            html += `<td class="col-left">`;
            if (key === 'table_name') {
                html += formatTableName(value);
            } else {
                html += formatValue(value, col.type, col.format);
            }
            html += '</td>';
        }
        html += '</tr>';
    });
    
    html += '</tbody></table></div>';
    tableContainer.innerHTML = html;
}

function formatTableName(tableName) {
    // 뱃지 표시 로직
    const badges = {
        'Quotation': '<span class="badge badge-primary">장비 견적서</span>',
        'Machine': '<span class="badge badge-primary">장비 견적서</span>',
        'Detailed': '<span class="badge badge-info">견적서(상세)</span>',
        'PriceCompare': '<span class="badge badge-warning">내정가 비교</span>',
        '비교 견적서': '<span class="badge badge-warning">내정가 비교</span>' // 한글 이름 대응
    };
    return badges[tableName] || tableName;
}

function formatDateTime(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}`;
}

function formatValue(value, type, format) {
    if (value === null || value === undefined || value === '') {
        return '<span class="text-muted">-</span>';
    }
    switch(type) {
        case 'datetime':
            if (format === 'YYYY-MM-DD HH:mm') return value.substring(0, 16).replace('T', ' ');
            return value;
        case 'date':
            return value.substring(0, 10).replace(/-/g, '. ');
        default:
            return value;
    }
}

async function submitGeneral() {
    const generalName = document.getElementById('generalName').value.trim();
    const client = document.getElementById('client').value.trim();
    const creator = document.getElementById('creator').value.trim();
    const description = document.getElementById('description').value.trim();
    
    if (!generalName) { alert('견적서명을 입력하세요.'); document.getElementById('generalName').focus(); return; }
    if (!creator) { alert('작성자명을 입력하세요.'); document.getElementById('creator').focus(); return; }
    
    const requestData = {
        name: generalName,
        client: client || null,
        creator: creator,
        description: description || null
    };
    
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.textContent = '등록 중...';
    
    try {
        const response = await fetch('/api/v1/quotation/general', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        
        if (response.ok) {
            const data = await response.json();
            alert(`견적서(일반)가 등록되었습니다!\nID: ${data.id}`);
            window.location.href = `/service/quotation/general/form?mode=view&id=${data.id}`;
        } else {
            const error = await response.json();
            alert('등록 실패: ' + (error.detail || JSON.stringify(error)));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('등록 중 오류가 발생했습니다.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = '등록완료';
    }
}

function goToList() {
    window.location.href = '/service/quotation/general';
}