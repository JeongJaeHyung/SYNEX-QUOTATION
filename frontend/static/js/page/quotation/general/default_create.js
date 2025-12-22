// ============================================================================
// 견적서(일반) 폼 스크립트 - default_create.js
// ============================================================================

// 페이지 모드 및 ID
let pageMode = 'create'; // create, view
let generalId = null;

// ============================================================================
// 페이지 초기화
// ============================================================================

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
    const derivativeBtnGroup = document.getElementById('derivativeBtnGroup');
    
    if (pageMode === 'create') {
        // 생성 모드
        titleElement.textContent = '견적서(일반) 생성';
        submitBtn.textContent = '등록완료';
        submitBtn.style.display = 'inline-block';
        viewOnlyFields.style.display = 'none';
        relationsSection.style.display = 'none';
        derivativeBtnGroup.style.display = 'none'; 
        
    } else if (pageMode === 'view') {
        // 조회 모드
        titleElement.textContent = '견적서(일반) 조회';
        submitBtn.style.display = 'none'; 
        viewOnlyFields.style.display = 'flex';
        relationsSection.style.display = 'block';
        derivativeBtnGroup.style.display = 'flex'; 
        
        disableAllInputs();
        
        if (generalId) {
            loadGeneralData(generalId);
            loadRelationsData(generalId);
        }
    }
}

// ============================================================================
// 모드 관리 및 데이터 로드
// ============================================================================

function disableAllInputs() {
    document.getElementById('generalName').readOnly = true;
    document.getElementById('client').readOnly = true;
    document.getElementById('creator').readOnly = true;
    document.getElementById('description').readOnly = true;
}

async function loadGeneralData(id) {
    try {
        const response = await fetch(`/api/v1/quotation/general/${id}`);
        if (!response.ok) throw new Error('데이터 로드 실패');
        
        const data = await response.json();
        const info = data.general || data;

        document.getElementById('generalName').value = info.name || '';
        document.getElementById('client').value = info.client || '';
        document.getElementById('creator').value = info.creator || '';
        document.getElementById('description').value = info.description || '';
        
        if (info.created_at) {
            document.getElementById('createdAt').value = formatDateTime(new Date(info.created_at));
        }
        if (info.updated_at) {
            document.getElementById('updatedAt').value = formatDateTime(new Date(info.updated_at));
        }
        
    } catch (error) {
        console.error('Error:', error);
        alert('데이터를 불러오는데 실패했습니다.');
    }
}

/**
 * 연관 테이블 데이터 로드 및 버튼 중복 제어 보완
 */
async function loadRelationsData(id) {
    const loading = document.getElementById('relationsLoading');
    const tableContainer = document.getElementById('relationsTableContainer');
    const priceCompareBtn = document.querySelector('.btn-primary[onclick="createPriceCompare()"]');
    
    loading.style.display = 'block';
    tableContainer.innerHTML = '';
    
    try {
        const response = await fetch(`/api/v1/quotation/general/${id}?include_relations=true`);
        if (!response.ok) throw new Error('연관 데이터 로드 실패');
        
        const data = await response.json();
        const items = data.related_documents || data.items || [];

        // [보완] 이미지(image_ce0fb6.png)의 구분값인 '비교 견적서'를 포함하여 체크
        const hasPriceCompare = items.some(item => 
            ['PriceCompare', '내정가비교', '비교 견적서', '내정가 비교'].includes(item.table_name || item.category)
        );

        // 이미 존재한다면 버튼을 즉시 숨김
        if (hasPriceCompare && priceCompareBtn) {
            priceCompareBtn.style.display = 'none';
        } else if (priceCompareBtn) {
            // 목록에 없을 때만 보이게 설정 (페이지 모드가 view일 때)
            if (pageMode === 'view') priceCompareBtn.style.display = 'inline-block';
        }

        // 테이블 렌더링 로직 유지...
        const schema = data.schema || {
            "category": { "title": "구분", "type": "string", "ratio": 1 },
            "title": { "title": "제목/비고", "type": "string", "ratio": 3 },
            "creator": { "title": "작성자", "type": "string", "ratio": 1 },
            "updated_at": { "title": "최종수정일", "type": "datetime", "format": "YYYY-MM-DD HH:mm", "ratio": 1.5 }
        };
        renderRelationsTable(schema, items);
        
    } catch (error) {
        console.error('Error:', error);
        tableContainer.innerHTML = '<div class="empty-state">연관 데이터를 불러오지 못했습니다.</div>';
    } finally {
        loading.style.display = 'none';
    }
}

// ============================================================================
// [중요 수정] 테이블 렌더링 및 클릭 이벤트 처리
// ============================================================================

function renderRelationsTable(schema, items) {
    const tableContainer = document.getElementById('relationsTableContainer');
    
    if (!items || items.length === 0) {
        tableContainer.innerHTML = '<div class="empty-state">연관된 견적서가 없습니다</div>';
        return;
    }
    
    let totalRatio = Object.values(schema).reduce((acc, col) => acc + (col.ratio || 1), 0);
    
    let html = '<div class="table-container"><table class="data-table" id="relationsTable">';
    html += '<thead><tr>';
    for (const key in schema) {
        const width = ((schema[key].ratio || 1) / totalRatio * 100).toFixed(1);
        html += `<th class="col-left" style="width: ${width}%">${schema[key].title}</th>`;
    }
    html += '</tr></thead><tbody>';
    
    items.forEach((item) => {
        // [수정] 행에 data-id와 data-table 속성을 부여하고 통합 핸들러 호출
        html += `
            <tr class="clickable" 
                data-id="${item.id}" 
                data-table="${item.table_name}" 
                onclick="handleRowClick(this)">`;
        
        for (const key in schema) {
            const col = schema[key];
            const value = item[key];
            html += `<td class="col-left">`;
            html += (key === 'table_name') ? formatTableName(value) : formatValue(value, col.type, col.format);
            html += '</td>';
        }
        html += '</tr>';
    });
    
    html += '</tbody></table></div>';
    tableContainer.innerHTML = html;
}

/**
 * 행 클릭 통합 핸들러 (ID 기반 API 요청 또는 페이지 이동)
 */
async function handleRowClick(rowElement) {
    // 1. 행의 data-id와 data-table 속성값 가져오기
    const id = rowElement.getAttribute('data-id');
    
    // [핵심 보완] data-table이 없거나 'undefined'일 경우를 대비해 
    // 내부 텍스트(구분 열)를 통해 타입을 한 번 더 추론합니다.
    let type = rowElement.getAttribute('data-table');
    const categoryText = rowElement.cells[0].textContent.trim(); 

    // 2. id가 없는 경우 예외 처리
    if (!id || id === 'undefined') {
        console.error("아이템 ID를 찾을 수 없습니다.");
        return;
    }

    // 3. 타입 판별 로직 (데이터 우선순위: data-table > 표시 텍스트)
    let detailUrl = '';
    
    // 상세 견적서(을지) 판별
    if (type === 'Detailed' || categoryText.includes('상세')) {
        detailUrl = `/service/quotation/general/detailed/detail/${id}`;
    } 
    // 내정가 비교표 판별
    else if (type === 'PriceCompare' || type === '비교 견적서' || categoryText.includes('비교')) {
        detailUrl = `/service/quotation/general/price_compare/detail/${id}`;
    }
    // 기본값 (기존 로직 유지)
    else {
        console.warn(`타입 판별 모호함(${type}), 기본 경로로 이동`);
        detailUrl = `/service/quotation/general/price_compare/detail/${id}`;
    }
    
    console.log(`페이지 이동 시도: ${detailUrl}`);
    window.location.href = detailUrl;
}

// ============================================================================
// 포맷팅 및 유틸리티
// ============================================================================

function formatTableName(tableName) {
    const badges = {
        'Quotation': '<span class="badge badge-primary">장비 견적서</span>',
        'Machine': '<span class="badge badge-primary">장비 견적서</span>',
        'Detailed': '<span class="badge badge-info">견적서(상세)</span>',
        'PriceCompare': '<span class="badge badge-warning">내정가 비교</span>',
        '비교 견적서': '<span class="badge badge-warning">내정가 비교</span>'
    };
    return badges[tableName] || tableName;
}

function formatDateTime(date) {
    const pad = (n) => String(n).padStart(2, '0');
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function formatValue(value, type, format) {
    if (value === null || value === undefined || value === '') return '<span class="text-muted">-</span>';
    switch(type) {
        case 'datetime':
            return (format === 'YYYY-MM-DD HH:mm') ? value.substring(0, 16).replace('T', ' ') : value;
        case 'date':
            return value.substring(0, 10).replace(/-/g, '. ');
        default:
            return value;
    }
}

// ============================================================================
// 액션 버튼 로직
// ============================================================================

function createPriceCompare() {
    if (!generalId) return alert('잘못된 접근입니다.');
    window.location.href = `/service/quotation/general/price_compare/register?general_id=${generalId}`;
}

async function submitGeneral() {
    const generalName = document.getElementById('generalName').value.trim();
    const client = document.getElementById('client').value.trim();
    const creator = document.getElementById('creator').value.trim();
    const description = document.getElementById('description').value.trim();
    
    if (!generalName || !creator) {
        alert('필수 항목(*)을 모두 입력하세요.');
        return;
    }
    
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
            alert(`등록되었습니다.`);
            window.location.href = `/service/quotation/general/form?mode=view&id=${data.id}`;
        } else {
            const error = await response.json();
            alert('등록 실패: ' + (error.detail || '오류 발생'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('서버 통신 중 오류가 발생했습니다.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = '등록완료';
    }
}

function goToList() {
    window.location.href = '/service/quotation/general';
}