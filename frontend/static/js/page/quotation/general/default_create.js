/**
 * 견적서(일반) 폼 스크립트 - 내정가 비교서 기반 장비 리스트 및 이동 경로 최적화 버전
 */
let pageMode = 'create'; 
let generalId = null;

document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    pageMode = urlParams.get('mode') || 'create';
    generalId = urlParams.get('id') || null;
    initializePage();
});

/**
 * 페이지 초기화: 모드에 따른 UI 설정
 */
function initializePage() {
    const titleElement = document.getElementById('pageTitle');
    const submitBtn = document.getElementById('submitBtn');
    const viewOnlyFields = document.getElementById('viewOnlyFields');
    const relationsSection = document.getElementById('relationsSection');
    const usedEquipmentSection = document.getElementById('usedEquipmentSection'); 
    const derivativeBtnGroup = document.getElementById('derivativeBtnGroup');
    
    if (pageMode === 'create') {
        titleElement.textContent = '견적서(일반) 생성';
        if (submitBtn) submitBtn.style.display = 'inline-block';
        if (viewOnlyFields) viewOnlyFields.style.display = 'none';
        if (relationsSection) relationsSection.style.display = 'none';
        if (usedEquipmentSection) usedEquipmentSection.style.display = 'none';
        if (derivativeBtnGroup) derivativeBtnGroup.style.display = 'none'; 
    } else if (pageMode === 'view') {
        titleElement.textContent = '견적서(일반) 조회';
        if (submitBtn) submitBtn.style.display = 'none'; 
        if (viewOnlyFields) viewOnlyFields.style.display = 'flex';
        if (relationsSection) relationsSection.style.display = 'block';
        if (usedEquipmentSection) usedEquipmentSection.style.display = 'block'; 
        if (derivativeBtnGroup) derivativeBtnGroup.style.display = 'flex'; 
        
        disableAllInputs();
        if (generalId) {
            loadGeneralData(generalId);
            loadRelationsData(generalId);
        }
    }
}

/**
 * 조회 모드 시 입력 필드 비활성화
 */
function disableAllInputs() {
    ['generalName', 'client', 'creator', 'description'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.readOnly = true;
    });
}

/**
 * 데이터 로드 및 연관 문서 분석
 */
async function loadRelationsData(id) {
    const relationsContainer = document.getElementById('relationsTableContainer');
    const loading = document.getElementById('relationsLoading');
    if (loading) loading.style.display = 'block';

    try {
        const response = await fetch(`/api/v1/quotation/general/${id}?include_relations=true`);
        const data = await response.json();
        const items = data.related_documents || data.items || [];

        // 1. 상단 상태 UI 업데이트 (갑지, 을지, 내정가 비교)
        updateStatusDisplay(items);

        // 2. [테이블 1] 전체 연관 견적서 목록 렌더링
        const mainSchema = data.schema || {
            "category": { "title": "구분", "type": "string" },
            "title": { "title": "제목/비고", "type": "string" },
            "creator": { "title": "작성자", "type": "string" },
            "updated_at": { "title": "최종수정일", "type": "datetime" }
        };
        renderRelationsTable(mainSchema, items);

        // 3. [핵심] 내정가 비교서가 있다면 상세 데이터를 조회하여 실제 장비 리스트 추출
        const compareDoc = items.find(i => i.table_name === 'PriceCompare' || (i.category && i.category.includes('내정가')));
        if (compareDoc) {
            fetchPriceCompareDetails(compareDoc.id);
        } else {
            document.getElementById('usedEquipmentTableContainer').innerHTML = 
                '<div class="empty-state">내정가 비교서가 생성되지 않아 장비 목록을 불러올 수 없습니다.</div>';
        }

    } catch (error) { 
        console.error('데이터 로드 실패', error);
        if (relationsContainer) relationsContainer.innerHTML = '데이터 로드 중 오류가 발생했습니다.'; 
    } finally {
        if (loading) loading.style.display = 'none';
    }
}

/**
 * 내정가 비교서 상세 API 조회 및 장비 목록 추출
 */
async function fetchPriceCompareDetails(compareId) {
    const usedContainer = document.getElementById('usedEquipmentTableContainer');
    try {
        const response = await fetch(`/api/v1/quotation/price_compare/${compareId}`);
        const data = await response.json();
        
        // 제공받은 JSON 구조에서 리소스 데이터 추출
        const resources = data.price_compare_resources || [];
        
        if (resources.length === 0) {
            usedContainer.innerHTML = '<div class="empty-state">비교서에 등록된 장비 데이터가 없습니다.</div>';
            return;
        }

        // machine_id 기준 중복 제거 및 장비 정보(ID, 이름) 매핑
        const equipmentMap = new Map();
        resources.forEach(res => {
            if (res.machine_id && !equipmentMap.has(res.machine_id)) {
                equipmentMap.set(res.machine_id, res.machine_name);
            }
        });

        const uniqueEquipments = Array.from(equipmentMap).map(([id, name]) => ({ id, name }));
        renderUsedEquipmentTable(usedContainer, uniqueEquipments);

    } catch (error) {
        console.error('PriceCompare Details Error', error);
        usedContainer.innerHTML = '<div class="empty-state">장비 정보를 불러오는 중 오류가 발생했습니다.</div>';
    }
}

/**
 * [테이블 2] 사용된 장비 견적서 목록 렌더링
 * 수정사항: 클릭 시 /service/quotation/machine/form 경로로 이동, "(을지)" 문구 제거
 */
function renderUsedEquipmentTable(container, equipments) {
    let html = '<table class="data-table"><thead><tr>' +
               '<th>No</th><th>장비 구분</th><th>장비 견적서명</th><th>상세 상태</th>' +
               '</tr></thead><tbody>';

    equipments.forEach((eq, idx) => {
        // [수정] 이동 경로: /service/quotation/machine/form?mode=view&id=
        // [수정] 표시 텍스트: (을지) 제거 및 실제 장비명 표시
        html += `<tr class="clickable" onclick="window.location.href='/service/quotation/machine/form?mode=view&id=${eq.id}'">` +
                `<td>${idx + 1}</td>` +
                `<td><span class="badge badge-info">장비 ${eq.name}</span></td>` +
                `<td style="font-weight: 600; color: #1e3a8a;">장비 견적서: ${eq.name}</td>` +
                `<td><span class="text-success" style="font-size: 12px; font-weight: 700;">● 비교 반영됨</span></td>` +
                `</tr>`;
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

/**
 * 상단 상태바 업데이트
 */
function updateStatusDisplay(items) {
    const hasHeader = items.some(i => i.table_name === 'header' || (i.category && i.category.includes('갑지')));
    const hasDetailed = items.some(i => i.table_name === 'Detailed' || (i.category && i.category.includes('을지')));
    const hasPC = items.some(i => i.table_name === 'PriceCompare' || (i.category && i.category.includes('내정가')));

    updateStatusText('statHeader', hasHeader);
    updateStatusText('statDetailed', hasDetailed);
    updateStatusText('statPriceCompare', hasPC);
}

function updateStatusText(elementId, isCreated) {
    const el = document.getElementById(elementId);
    if (!el) return;
    if (isCreated) {
        el.textContent = '생성됨';
        el.className = 'status-text text-success';
    } else {
        el.textContent = '없음';
        el.className = 'status-text text-muted';
    }
}

/**
 * 테이블 1: 연관 견적서 전체 목록 렌더링
 */
function renderRelationsTable(schema, items) {
    const container = document.getElementById('relationsTableContainer');
    if (!items || items.length === 0) {
        container.innerHTML = '<div class="empty-state">연관된 견적서가 없습니다</div>';
        return;
    }
    let html = '<table class="data-table"><thead><tr>';
    for (const key in schema) html += `<th>${schema[key].title}</th>`;
    html += '</tr></thead><tbody>';
    items.forEach(item => {
        html += `<tr class="clickable" onclick="handleRowClick('${item.id}', '${item.table_name}', '${item.category}')">`;
        for (const key in schema) {
            let val = item[key] || '-';
            if (schema[key].type === 'datetime' && val !== '-') val = val.substring(0, 16).replace('T', ' ');
            html += `<td>${val}</td>`;
        }
        html += '</tr>';
    });
    container.innerHTML = html + '</tbody></table>';
}

/**
 * 행 클릭 시 상세 페이지 이동 분기 (전체 목록용)
 */
function handleRowClick(id, type, category) {
    if (!id || id === 'undefined') return;
    let url = '';
    const isDetailed = (type === 'Detailed' || (category && (category.includes('상세') || category.includes('을지'))));
    const isHeader = (type === 'header' || type === 'Cover' || (category && category.includes('갑지')));

    if (isDetailed) {
        url = `/service/quotation/general/detailed/detail/${id}`;
    } else if (isHeader) {
        url = `/service/quotation/general/header/detail/${id}`;
    } else {
        url = `/service/quotation/general/price_compare/detail/${id}`;
    }
    window.location.href = url;
}

/**
 * 일반 정보 등록 및 로드
 */
async function submitGeneral() {
    const requestData = {
        name: document.getElementById('generalName').value.trim(),
        client: document.getElementById('client').value.trim() || null,
        creator: document.getElementById('creator').value.trim(),
        description: document.getElementById('description').value.trim() || null
    };
    if (!requestData.name || !requestData.creator) return alert('필수 항목을 입력하세요.');

    try {
        const res = await fetch('/api/v1/quotation/general', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        if (res.ok) {
            const data = await res.json();
            alert('등록되었습니다.');
            window.location.href = `/service/quotation/general/form?mode=view&id=${data.id}`;
        }
    } catch (e) { alert('서버 통신 오류'); }
}

async function loadGeneralData(id) {
    try {
        const res = await fetch(`/api/v1/quotation/general/${id}`);
        const data = await res.json();
        const info = data.general || data;
        document.getElementById('generalName').value = info.name || '';
        document.getElementById('client').value = info.client || '';
        document.getElementById('creator').value = info.creator || '';
        document.getElementById('description').value = info.description || '';
        if (info.created_at) document.getElementById('createdAt').value = info.created_at.substring(0, 16).replace('T', ' ');
        if (info.updated_at) document.getElementById('updatedAt').value = info.updated_at.substring(0, 16).replace('T', ' ');
    } catch (e) { console.error('정보 로드 실패'); }
}

// 이동 함수
function createDetailed() { window.location.href = `/service/quotation/general/detailed/register?general_id=${generalId}`; }
function createHeader() { window.location.href = `/service/quotation/general/header/register?general_id=${generalId}`; }
function createPriceCompare() { window.location.href = `/service/quotation/general/price_compare/register?general_id=${generalId}`; }
function goToList() { window.location.href = '/service/quotation/general'; }