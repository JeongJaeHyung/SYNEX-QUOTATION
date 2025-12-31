/**
 * 견적서(일반) 폼 스크립트 - 내정가 비교서 기반 장비 리스트 및 이동 경로 최적화 버전
 */
let pageMode = 'create';
let generalId = null;
let generalName = '';  // 전역 변수로 general name 저장
let foldersData = [];  // 전역 변수로 folders 데이터 저장

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
    const folderSection = document.getElementById('folderSection');
    const usedEquipmentSection = document.getElementById('usedEquipmentSection');

    if (pageMode === 'create') {
        titleElement.textContent = '견적서(일반) 생성';
        if (submitBtn) submitBtn.style.display = 'inline-block';
        if (viewOnlyFields) viewOnlyFields.style.display = 'none';
        if (folderSection) folderSection.style.display = 'none';
        if (usedEquipmentSection) usedEquipmentSection.style.display = 'none';
    } else if (pageMode === 'view') {
        titleElement.textContent = '견적서(일반) 조회';
        if (submitBtn) submitBtn.style.display = 'none';
        if (viewOnlyFields) viewOnlyFields.style.display = 'flex';
        if (folderSection) folderSection.style.display = 'block';
        if (usedEquipmentSection) usedEquipmentSection.style.display = 'block';

        // 수정 버튼 표시
        const editBtn = document.getElementById('editBtn');
        if (editBtn) editBtn.style.display = 'inline-block';

        disableAllInputs();
        if (generalId) {
            loadGeneralData(generalId);
            loadFolders(generalId);
            fetchAllFolderEquipments(generalId);
        }
    }
}

/**
 * 조회 모드 시 입력 필드 비활성화
 */
function disableAllInputs() {
    ['generalName', 'client', 'creator', 'manufacturer', 'description'].forEach(id => {
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

        // 3. [핵심] 모든 폴더의 내정가 비교서를 조회하여 장비 리스트 추출
        fetchAllFolderEquipments(generalId);

    } catch (error) { 
        console.error('데이터 로드 실패', error);
        if (relationsContainer) relationsContainer.innerHTML = '데이터 로드 중 오류가 발생했습니다.'; 
    } finally {
        if (loading) loading.style.display = 'none';
    }
}

/**
 * 모든 폴더의 내정가 비교서에서 장비 목록 추출
 */
async function fetchAllFolderEquipments(generalId) {
    const usedContainer = document.getElementById('usedEquipmentTableContainer');

    try {
        // 1. 모든 폴더 가져오기
        const generalResponse = await fetch(`/api/v1/quotation/general/${generalId}?include_relations=true`);
        const generalData = await generalResponse.json();
        const folderIds = generalData.folders || [];

        if (folderIds.length === 0) {
            usedContainer.innerHTML = '<div class="empty-state">폴더가 없습니다.</div>';
            return;
        }

        // 2. 각 폴더의 정보와 내정가 비교서 가져오기
        const equipmentsByFolder = [];

        for (const folderId of folderIds) {
            const folderResponse = await fetch(`/api/v1/quotation/folder/${folderId}?include_resources=true`);
            const folderData = await folderResponse.json();

            // 폴더의 내정가 비교서 찾기
            const priceCompare = (folderData.resources || []).find(r => r.table_name === '내정가 비교');

            if (priceCompare) {
                // 내정가 비교서의 상세 데이터 가져오기
                const compareResponse = await fetch(`/api/v1/quotation/price_compare/${priceCompare.id}`);
                const compareData = await compareResponse.json();
                const resources = compareData.price_compare_resources || [];

                // machine_id 기준 중복 제거
                const equipmentMap = new Map();
                resources.forEach(res => {
                    if (res.machine_id && !equipmentMap.has(res.machine_id)) {
                        equipmentMap.set(res.machine_id, res.machine_name);
                    }
                });

                // 폴더명과 장비 정보 결합
                equipmentMap.forEach((machineName, machineId) => {
                    equipmentsByFolder.push({
                        folderId: folderId,
                        folderTitle: folderData.title,
                        machineId: machineId,
                        machineName: machineName
                    });
                });
            }
        }

        if (equipmentsByFolder.length === 0) {
            usedContainer.innerHTML = '<div class="empty-state">내정가 비교서에 등록된 장비가 없습니다.</div>';
            return;
        }

        renderUsedEquipmentTable(usedContainer, equipmentsByFolder);

    } catch (error) {
        console.error('장비 정보 로드 오류:', error);
        usedContainer.innerHTML = '<div class="empty-state">장비 정보를 불러오는 중 오류가 발생했습니다.</div>';
    }
}

/**
 * [테이블 2] 사용된 장비 견적서 목록 렌더링
 * 수정사항: 폴더명과 장비명 표시, 클릭 시 /service/quotation/machine/form 경로로 이동
 */
function renderUsedEquipmentTable(container, equipments) {
    let html = '<table class="data-table"><thead><tr>' +
               '<th>No</th><th>폴더</th><th>장비명</th><th>장비 견적서명</th><th>상세 상태</th>' +
               '</tr></thead><tbody>';

    equipments.forEach((eq, idx) => {
        // 장비 견적서 페이지로 이동
        html += `<tr class="clickable" onclick="window.location.href='/service/quotation/machine/form?mode=view&id=${eq.machineId}'">` +
                `<td>${idx + 1}</td>` +
                `<td><span class="badge badge-primary" style="background: #3b82f6;">📁 ${eq.folderTitle}</span></td>` +
                `<td><span class="badge badge-info" style="background: #06b6d4;">${eq.machineName}</span></td>` +
                `<td style="font-weight: 600; color: #1e3a8a;">장비 견적서: ${eq.machineName}</td>` +
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
        manufacturer: document.getElementById('manufacturer').value.trim(),
        description: document.getElementById('description').value.trim() || null
    };
    if (!requestData.name || !requestData.creator || !requestData.manufacturer) return alert('필수 항목을 입력하세요.');

    try {
        // 수정 모드인 경우
        if (pageMode === 'view' && generalId) {
            const res = await fetch(`/api/v1/quotation/general/${generalId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });
            if (res.ok) {
                alert('수정되었습니다.');
                window.location.reload();
            }
        } else {
            // 생성 모드
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
        }
    } catch (e) { alert('서버 통신 오류'); }
}

async function loadGeneralData(id) {
    try {
        const res = await fetch(`/api/v1/quotation/general/${id}`);
        const data = await res.json();
        const info = data.general || data;
        generalName = info.name || '';  // 전역 변수에 저장
        document.getElementById('generalName').value = generalName;
        document.getElementById('client').value = info.client || '';
        document.getElementById('creator').value = info.creator || '';
        document.getElementById('manufacturer').value = info.manufacturer || '';
        document.getElementById('description').value = info.description || '';
        if (info.created_at) document.getElementById('createdAt').value = info.created_at.substring(0, 16).replace('T', ' ');
        if (info.updated_at) document.getElementById('updatedAt').value = info.updated_at.substring(0, 16).replace('T', ' ');
    } catch (e) { console.error('정보 로드 실패'); }
}

// 이동 함수
function goToList() { window.location.href = '/service/quotation/general'; }

/**
 * 폴더 시스템 관련 함수들
 */
async function loadFolders(generalId) {
    const container = document.getElementById('foldersContainer');
    try {
        const response = await fetch(`/api/v1/quotation/general/${generalId}?include_relations=true`);
        const data = await response.json();
        const folderIds = data.folders || [];

        if (folderIds.length === 0) {
            container.innerHTML = '<div class="empty-state">폴더가 없습니다. 폴더를 생성하여 견적서를 관리하세요.</div>';
            return;
        }

        // 각 폴더 데이터 로드
        const folders = await Promise.all(
            folderIds.map(async (folderId) => {
                const res = await fetch(`/api/v1/quotation/folder/${folderId}?include_resources=true`);
                return await res.json();
            })
        );

        renderFolders(folders);
    } catch (error) {
        console.error('폴더 로드 실패:', error);
        container.innerHTML = '<div class="empty-state" style="color: #ef4444;">폴더를 불러오는데 실패했습니다.</div>';
    }
}

function renderFolders(folders) {
    const container = document.getElementById('foldersContainer');
    foldersData = folders;  // 전역 변수에 저장
    let html = '';

    folders.forEach(folder => {
        const resources = folder.resources || [];
        // table_name으로 리소스 찾기
        const priceCompare = resources.find(r => r.table_name === '내정가 비교');
        const detailed = resources.find(r => r.table_name === '견적서(을지)');
        const header = resources.find(r => r.table_name === '견적서');

        html += `
            <div class="folder-card">
                <div class="folder-header">
                    <div class="folder-title-section">
                        <span>📁</span>
                        <h4 class="folder-title">${folder.title}</h4>
                    </div>
                    <div class="folder-actions">
                        <button class="btn-icon" onclick="downloadFolderExcel('${folder.id}')" title="폴더 전체 Excel 저장">📊 Excel</button>
                        <button class="btn-icon" onclick="downloadFolderPDF('${folder.id}')" title="폴더 전체 PDF 저장">📄 PDF</button>
                        <button class="btn-icon" onclick="deleteFolder('${folder.id}')" title="폴더 삭제">🗑️</button>
                    </div>
                </div>
                <div class="folder-body">
                    <div class="resource-list">
                        ${renderResourceItem('price_compare', '내정가 비교서', priceCompare, folder.id, folder.title)}
                        ${renderResourceItem('detailed', '을지', detailed, folder.id, folder.title)}
                        ${renderResourceItem('header', '갑지', header, folder.id, folder.title)}
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

function renderResourceItem(type, typeName, resource, folderId, folderTitle) {
    if (resource) {
        // 리소스가 있는 경우
        return `
            <div class="resource-item">
                <div class="resource-type">${typeName}</div>
                <div class="resource-status">
                    <span class="status-badge created">생성됨</span>
                    <div class="resource-actions-btn">
                        <button class="btn-icon" onclick="downloadResourceExcel('${type}', '${resource.id}', '${folderTitle}')" title="Excel 다운로드">📊</button>
                        <button class="btn-icon" onclick="downloadResourcePDF('${type}', '${resource.id}', '${folderTitle}')" title="PDF 다운로드">📄</button>
                        <button class="btn-icon" onclick="deleteResource('${type}', '${resource.id}', '${folderId}')" title="삭제">🗑️</button>
                    </div>
                </div>
                <div style="font-size: 13px; font-weight: 600; color: #1f2937; margin-top: 8px; cursor: pointer; text-decoration: underline;"
                     onclick="viewResource('${type}', '${resource.id}')"
                     title="클릭하여 상세보기">
                    ${resource.title || '제목 없음'}
                </div>
                <div style="font-size: 12px; color: #6b7280; margin-top: 4px;">
                    ${new Date(resource.updated_at).toLocaleString('ko-KR')}
                </div>
            </div>
        `;
    } else {
        // 리소스가 없는 경우
        return `
            <div class="resource-item">
                <div class="resource-type">${typeName}</div>
                <div class="resource-status">
                    <span class="status-badge empty">미생성</span>
                </div>
                <button class="btn-create" onclick="createResource('${type}', '${folderId}')">
                    + ${typeName} 만들기
                </button>
            </div>
        `;
    }
}

// 폴더 생성 모달 열기/닫기
function openCreateFolderModal() {
    document.getElementById('createFolderModal').style.display = 'flex';
    document.getElementById('folderTitle').value = '';
}

function closeFolderModal() {
    document.getElementById('createFolderModal').style.display = 'none';
}

// 폴더 생성
async function submitCreateFolder() {
    const title = document.getElementById('folderTitle').value.trim();
    if (!title) {
        alert('폴더 제목을 입력하세요.');
        return;
    }

    try {
        const response = await fetch('/api/v1/quotation/folder', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                general_id: generalId,
                title: title
            })
        });

        if (response.ok) {
            alert('폴더가 생성되었습니다.');
            closeFolderModal();
            loadFolders(generalId);
        } else {
            const error = await response.json();
            alert('폴더 생성 실패: ' + (error.detail || '알 수 없는 오류'));
        }
    } catch (error) {
        console.error('폴더 생성 오류:', error);
        alert('서버 통신 오류');
    }
}

// 폴더 삭제
async function deleteFolder(folderId) {
    if (!confirm('폴더와 내부의 모든 견적서가 삭제됩니다. 계속하시겠습니까?')) return;

    try {
        const response = await fetch(`/api/v1/quotation/folder/${folderId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            alert('폴더가 삭제되었습니다.');
            loadFolders(generalId);
        } else {
            alert('폴더 삭제 실패');
        }
    } catch (error) {
        console.error('폴더 삭제 오류:', error);
        alert('서버 통신 오류');
    }
}

// 리소스 생성
function createResource(type, folderId) {
    let url = '';
    switch(type) {
        case 'price_compare':
            url = `/service/quotation/general/price_compare/register?folder_id=${folderId}`;
            break;
        case 'detailed':
            url = `/service/quotation/general/detailed/register?folder_id=${folderId}`;
            break;
        case 'header':
            url = `/service/quotation/general/header/register?folder_id=${folderId}`;
            break;
    }
    window.location.href = url;
}

// 리소스 보기
function viewResource(type, resourceId) {
    let url = '';
    switch(type) {
        case 'price_compare':
            url = `/service/quotation/general/price_compare/detail/${resourceId}`;
            break;
        case 'detailed':
            url = `/service/quotation/general/detailed/detail/${resourceId}`;
            break;
        case 'header':
            url = `/service/quotation/general/header/detail/${resourceId}`;
            break;
    }
    window.location.href = url;
}

// 리소스 삭제
async function deleteResource(type, resourceId, folderId) {
    if (!confirm('이 견적서를 삭제하시겠습니까?')) return;

    let apiPath = '';
    switch(type) {
        case 'price_compare':
            apiPath = `/api/v1/quotation/price_compare/${resourceId}`;
            break;
        case 'detailed':
            apiPath = `/api/v1/quotation/detailed/${resourceId}`;
            break;
        case 'header':
            apiPath = `/api/v1/quotation/header/${resourceId}`;
            break;
    }

    try {
        const response = await fetch(apiPath, {
            method: 'DELETE'
        });

        if (response.ok) {
            alert('견적서가 삭제되었습니다.');
            loadFolders(generalId);
        } else {
            alert('삭제 실패');
        }
    } catch (error) {
        console.error('삭제 오류:', error);
        alert('서버 통신 오류');
    }
}

/**
 * Excel/PDF 다운로드 함수들
 */

// 개별 리소스 Excel 저장
async function downloadResourceExcel(type, resourceId, folderTitle) {
    let apiPath = '';
    let docType = '';

    switch(type) {
        case 'price_compare':
            apiPath = `/api/v1/export/excel/price_compare/${resourceId}`;
            docType = '내정가비교서';
            break;
        case 'detailed':
            apiPath = `/api/v1/export/excel/detailed/${resourceId}`;
            docType = '을지';
            break;
        case 'header':
            apiPath = `/api/v1/export/excel/header/${resourceId}`;
            docType = '갑지';
            break;
    }

    try {
        const response = await fetch(apiPath, {
            method: 'GET'
        });

        if (!response.ok) {
            throw new Error(`Excel 생성 실패: ${response.status}`);
        }

        const result = await response.json();

        if (result.success) {
            alert('Excel 파일이 저장되었습니다:\n' + result.path);
        } else {
            alert('저장 실패: ' + (result.message || '알 수 없는 오류'));
        }
    } catch (error) {
        console.error('Excel 저장 오류:', error);
        alert('Excel 파일 저장 중 오류가 발생했습니다.');
    }
}

// 개별 리소스 PDF 다운로드
async function downloadResourcePDF(type, resourceId, folderTitle) {
    let detailUrl = '';
    let docType = '';

    switch(type) {
        case 'price_compare':
            detailUrl = `/service/quotation/general/price_compare/detail/${resourceId}`;
            docType = '내정가비교서';
            break;
        case 'detailed':
            detailUrl = `/service/quotation/general/detailed/detail/${resourceId}`;
            docType = '을지';
            break;
        case 'header':
            detailUrl = `/service/quotation/general/header/detail/${resourceId}`;
            docType = '갑지';
            break;
    }

    const timestamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14);
    const filename = `${docType}_${timestamp}.pdf`;

    // 디버그: PDF export 파라미터 출력
    console.log('[PDF Export] generalName:', generalName);
    console.log('[PDF Export] folderTitle:', folderTitle);
    console.log('[PDF Export] docType:', docType);
    console.log('[PDF Export] filename:', filename);

    try {
        const response = await fetch('/api/save-pdf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: window.location.origin + detailUrl,
                filename: filename,
                projectName: docType,
                docType: docType,
                generalName: generalName,  // 전역 변수 사용
                folderTitle: folderTitle   // 파라미터로 받은 폴더명
            })
        });

        const result = await response.json();
        if (result.success) {
            alert('PDF가 저장되었습니다:\n' + result.path);
        } else if (result.message !== '저장이 취소되었습니다.') {
            alert('저장 실패: ' + result.message);
        }
    } catch (error) {
        console.error('PDF 저장 오류:', error);
        alert('PDF 저장 중 오류가 발생했습니다.');
    }
}

// 폴더 전체 Excel 저장 (갑지, 을지, 내정가비교서 순서로 시트 생성)
async function downloadFolderExcel(folderId) {
    try {
        const response = await fetch(`/api/v1/export/excel/folder/${folderId}`, {
            method: 'GET'
        });

        if (!response.ok) {
            throw new Error(`Excel 생성 실패: ${response.status}`);
        }

        const result = await response.json();

        if (result.success) {
            alert('Excel 파일이 저장되었습니다:\n' + result.path);
        } else {
            alert('저장 실패: ' + (result.message || '알 수 없는 오류'));
        }
    } catch (error) {
        console.error('Excel 저장 오류:', error);
        alert('Excel 파일 저장 중 오류가 발생했습니다.');
    }
}

// 폴더 전체 PDF 다운로드 (갑지, 을지, 내정가비교서 순서로 결합)
async function downloadFolderPDF(folderId) {
    try {
        const response = await fetch(`/api/v1/export/pdf/folder/${folderId}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/pdf'
            }
        });

        if (!response.ok) {
            throw new Error(`PDF 생성 실패: ${response.status}`);
        }

        const blob = await response.blob();
        const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '');
        const filename = `폴더통합견적서_${timestamp}.pdf`;

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        console.error('PDF 다운로드 오류:', error);
        alert('PDF 파일 다운로드 중 오류가 발생했습니다.');
    }
}

/**
 * 편집 모드 토글
 */
let originalData = {}; // 원본 데이터 저장

function toggleEditMode() {
    // 원본 데이터 저장
    originalData = {
        name: document.getElementById('generalName').value,
        client: document.getElementById('client').value,
        creator: document.getElementById('creator').value,
        manufacturer: document.getElementById('manufacturer').value,
        description: document.getElementById('description').value
    };

    // 입력 필드 활성화
    ['generalName', 'client', 'creator', 'manufacturer', 'description'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.disabled = false;
    });

    // 버튼 상태 변경
    document.getElementById('editBtn').style.display = 'none';
    document.getElementById('submitBtn').style.display = 'inline-block';
    document.getElementById('cancelBtn').style.display = 'inline-block';
    document.getElementById('submitBtn').textContent = '수정완료';
}

/**
 * 편집 취소
 */
function cancelEdit() {
    // 원본 데이터 복원
    document.getElementById('generalName').value = originalData.name;
    document.getElementById('client').value = originalData.client;
    document.getElementById('creator').value = originalData.creator;
    document.getElementById('manufacturer').value = originalData.manufacturer;
    document.getElementById('description').value = originalData.description;

    // 입력 필드 비활성화
    disableAllInputs();

    // 버튼 상태 변경
    document.getElementById('editBtn').style.display = 'inline-block';
    document.getElementById('submitBtn').style.display = 'none';
    document.getElementById('cancelBtn').style.display = 'none';
}