let partsData = [];
let selectedParts = new Map();
let selectedOrder = [];
let pendingInsertIndex = null;
let partsViewMode = 'ALL'; // 'ALL'(전체 보기) | 'TEMPLATE'(템플릿 보기)
let currentPartsDisplayOrder = [];
let currentSortKey = null;
let currentSortOrder = 'asc';

// [수정] 수동 항목 관리 객체에 id 필드 추가 (API에서 받아온 실제 ID 저장용)
let manualSummaryItems = {
    LOCAL_MAT: { id: null, price: 0, quantity: 0, subtotal: 0 },
    OPERATION_PC: { id: null, price: 0, quantity: 0, subtotal: 0 },
    CABLE_ETC: { id: null, price: 0, quantity: 0, subtotal: 0 }  // [신규] 케이블 및 기타 잡자재
};
let laborItems = []; 

// 자동 저장 관련 변수
let isDirty = false;
let autoSaveInterval = null;
const AUTO_SAVE_DELAY = 60000; // 60초
let isSaving = false; // 저장 중 여부 (중복 저장 방지)

// 페이지 모드 및 ID
let pageMode = 'create'; 
let machineId = null;

// 기존 장비(템플릿) 불러오기 상태
let importMachines = [];
let importSelectedId = null;
let importSelectedName = null;

document.addEventListener('DOMContentLoaded', async function() {
    const urlParams = new URLSearchParams(window.location.search);
    pageMode = urlParams.get('mode') || 'create';
    machineId = urlParams.get('id') || null;
    
    initializePage();
    
    // 💡 [수정] loadParts()는 반드시 await 되어야 합니다.
    // loadParts() 내에서 T000 ID 매핑이 완료되도록 보장합니다.
    await loadParts(); // 이 시점에서 manualSummaryItems.CABLE_ETC.id 등이 채워져야 합니다.
    
    if (machineId) {
        // 💡 [수정] loadParts()가 완료된 후에만 machineData를 로드합니다.
        await loadMachineData(machineId);
    }
    
    updateSummary();
    renderPartsTable();
    
    // [신규] 변경 감지 및 자동 저장 초기화
    initAutoSave();
});

function setPartsViewMode(mode) {
    partsViewMode = mode;

    const titleEl = document.querySelector('.action-bar .action-bar-left h3');
    const toggleBtn = document.getElementById('togglePartsViewBtn');

    if (titleEl) {
        titleEl.textContent = partsViewMode === 'TEMPLATE' ? '템플릿 보기' : '전체 보기';
    }
    if (toggleBtn) {
        toggleBtn.textContent = partsViewMode === 'TEMPLATE' ? '전체 보기' : '템플릿 보기';
        toggleBtn.disabled = (partsViewMode !== 'TEMPLATE' && selectedOrder.length === 0);
    }
}

function togglePartsView() {
    if (partsViewMode === 'TEMPLATE') {
        setPartsViewMode('ALL');
        loadParts();
        return;
    }
    if (selectedOrder.length === 0) {
        alert('템플릿/선택된 부품이 없습니다.');
        return;
    }
    setPartsViewMode('TEMPLATE');
    renderPartsTable();
    renderLaborItems(); // [신규] 뷰 모드 변경 시 인건비 목록도 갱신
    updateCategoryFilterOptions(); // [신규] 필터 옵션 갱신
}

function renderPartsTable() {
    if (partsViewMode === 'TEMPLATE') {
        renderTemplatePartsTable();
        return;
    }
    renderTable(null, partsData);
}

function initAutoSave() {
    // 모든 입력 필드에 변경 감지 리스너 추가
    document.body.addEventListener('input', (e) => {
        if (e.target.matches('input, select, textarea')) {
            markAsDirty();
        }
    });
    
    // 장비명이 입력되면 자동 저장 타이머 시작
    const nameInput = document.getElementById('machineName');
    if (nameInput) {
        nameInput.addEventListener('input', () => {
            if (!autoSaveInterval && nameInput.value.trim()) {
                startAutoSaveTimer();
            }
        });
        // 이미 값이 있으면 시작 (수정 모드 등)
        if (nameInput.value.trim()) {
            startAutoSaveTimer();
        }
    }
}

function markAsDirty() {
    isDirty = true;
    const status = document.getElementById('autoSaveStatus');
    if (status) status.textContent = '저장되지 않은 변경사항이 있습니다';
}

function startAutoSaveTimer() {
    if (autoSaveInterval) return;
    console.log('자동 저장 타이머 시작');
    autoSaveInterval = setInterval(() => {
        if (isDirty) {
            saveDraft(true); // Silent 모드로 저장
        }
    }, AUTO_SAVE_DELAY);
}

function initializePage() {
    const titleElement = document.querySelector('.create-header h2');
    const submitBtn = document.getElementById('submitBtn');
    const fabSubmitBtn = document.getElementById('fabSubmitBtn');
    const fabEditBtn = document.getElementById('fabEditBtn');
    const fabSaveBtn = document.getElementById('fabSaveBtn'); // [신규] 임시저장 버튼
    const actionButtons = document.querySelector('.action-footer');
    const importBtn = document.getElementById('importBtn');
    
    if (pageMode === 'create') {
        titleElement.textContent = '장비 견적서 생성';
        submitBtn.textContent = '등록완료';
        submitBtn.onclick = submitMachine;
        
        if (fabSubmitBtn) {
            fabSubmitBtn.onclick = submitMachine;
            fabSubmitBtn.style.display = '';
        }
        if (fabEditBtn) fabEditBtn.style.display = 'none';
        if (fabSaveBtn) fabSaveBtn.style.display = ''; // [신규] 생성 모드: 보임
        
        if (importBtn) importBtn.style.display = '';
        
        document.getElementById('totalPrice').readOnly = true;
        document.getElementById('createdAt').readOnly = true;
        document.getElementById('updatedAt').readOnly = true;
        
    } else if (pageMode === 'view') {
        titleElement.textContent = '장비 견적서 조회';
        disableAllInputs();
        if (importBtn) importBtn.style.display = 'none';
        
        if (fabSubmitBtn) fabSubmitBtn.style.display = 'none';
        if (fabEditBtn) fabEditBtn.style.display = '';
        if (fabSaveBtn) fabSaveBtn.style.display = 'none'; // [신규] 조회 모드: 숨김
        
        actionButtons.innerHTML = `
            <button class="btn btn-secondary btn-lg" onclick="goBack()">목록으로</button>
            <button class="btn btn-primary btn-lg" onclick="switchToEditMode()">수정하기</button>
        `;
        
    } else if (pageMode === 'edit') {
        titleElement.textContent = '장비 견적서 수정';
        submitBtn.textContent = '수정완료';
        submitBtn.onclick = updateMachine;
        
        if (fabSubmitBtn) {
            fabSubmitBtn.onclick = updateMachine;
            fabSubmitBtn.style.display = '';
        }
        if (fabEditBtn) fabEditBtn.style.display = 'none';
        if (fabSaveBtn) fabSaveBtn.style.display = ''; // [신규] 수정 모드: 보임
        
        if (importBtn) importBtn.style.display = 'none';
        
        document.getElementById('totalPrice').readOnly = true;
        document.getElementById('createdAt').readOnly = true;
        document.getElementById('updatedAt').readOnly = true;
        
        actionButtons.querySelector('.btn-secondary').textContent = '취소';
    }
}

function disableAllInputs() {
    document.getElementById('machineName').readOnly = true;
    document.getElementById('manufacturer').readOnly = true;
    document.getElementById('client').readOnly = true;
    document.getElementById('creator').readOnly = true;
    document.getElementById('description').readOnly = true;
    
    // document.getElementById('categoryFilter').disabled = true; // [수정] 조회 모드에서도 필터 허용
    // document.getElementById('searchInput').disabled = true; // [수정] 조회 모드에서도 검색 허용
    // document.querySelector('.action-bar-right .btn-primary').disabled = true; // [수정] 조회 모드에서도 검색 허용
    
    document.querySelectorAll('.manual-summary-input').forEach(input => {
        input.readOnly = true;
        input.style.backgroundColor = '#f9fafb';
        input.style.cursor = 'not-allowed';
    });
}

function switchToEditMode() {
    window.location.href = `?mode=edit&id=${machineId}`;
}

async function loadMachineData(id) {
    try {
        const response = await fetch(`/api/v1/quotation/machine/${id}?include_schema=true`);
        if (!response.ok) throw new Error('데이터 로드 실패');
        const data = await response.json();
    
        document.getElementById('machineName').value = data.name || '';
        document.getElementById('manufacturer').value = data.manufacturer || '';
        document.getElementById('client').value = data.client || '';
        document.getElementById('creator').value = data.creator || '';
        document.getElementById('description').value = data.description || '';
        document.getElementById('totalPrice').value = (data.total_price || 0).toLocaleString('ko-KR') + '원';
        
        if (data.created_at) document.getElementById('createdAt').value = formatDateTime(new Date(data.created_at));
        if (data.updated_at) document.getElementById('updatedAt').value = formatDateTime(new Date(data.updated_at));
        applyMachineResourcesToForm(data);
        
    } catch (error) {
        console.error('Error:', error);
        alert('데이터를 불러오는데 실패했습니다.');
    }
}

function applyMachineResourcesToForm(machineDetailData) {
    const resources = machineDetailData.resources?.items || machineDetailData.resources || [];

    // 기존 상태 초기화
    selectedParts = new Map();
    selectedOrder = [];
    pendingInsertIndex = null;
    updateInsertStatus();

    // 수동 항목 초기화
    Object.keys(manualSummaryItems).forEach(k => {
        manualSummaryItems[k].price = 0;
        manualSummaryItems[k].quantity = 0;
        manualSummaryItems[k].subtotal = 0;
    });

    // 인건비 초기화 (price는 마스터 기본값 유지)
    laborItems.forEach(item => {
        item.quantity = 0;
        item.subtotal = 0;
        item.isTemplate = false; // [신규] 템플릿 포함 여부 초기화
    });

    resources.forEach(resource => {
        const itemCode = resource.item_code;

        // T000 시리즈 (집계 항목 및 인건비)
        if (resource.maker_id === 'SUMMARY' || resource.maker_id === 'T000') {
            // 1) 수동 항목 확인 (ID로 매칭)
            if (resource.resources_id === manualSummaryItems.LOCAL_MAT.id) {
                updateManualItemFromDB('LOCAL_MAT', resource);
                return;
            }
            if (resource.resources_id === manualSummaryItems.OPERATION_PC.id) {
                updateManualItemFromDB('OPERATION_PC', resource);
                return;
            }
            if (resource.resources_id === manualSummaryItems.CABLE_ETC.id) {
                updateManualItemFromDB('CABLE_ETC', resource);
                return;
            }       
            // 2) 인건비 항목 확인
            const targetItem = laborItems.find(i => i.id === resource.resources_id);
            if (targetItem) {
                targetItem.price = resource.solo_price;
                targetItem.quantity = resource.quantity;
                targetItem.subtotal = resource.solo_price * resource.quantity;
                targetItem.isTemplate = true; // [신규] 템플릿에 포함된 항목임
                return;
            }
        }
        // 그 외 일반 부품
        // resource 객체에 id 필드가 없으면 resources_id를 id로 매핑
        const partData = { ...resource };
        if (!partData.id && partData.resources_id) {
            partData.id = partData.resources_id;
        }

        selectedParts.set(itemCode, {
            part: partData,
            quantity: resource.quantity,
            solo_price: resource.solo_price,
            subtotal: resource.solo_price * resource.quantity
        });

        if (!selectedOrder.includes(itemCode)) {
            selectedOrder.push(itemCode);
        }
    });

    setPartsViewMode('TEMPLATE');
    renderPartsTable();
    renderLaborItems();
    updateSummary();
    updateCategoryFilterOptions(); // [신규] 카테고리 필터 옵션 갱신
}

function updateManualItemFromDB(key, resource) {
    manualSummaryItems[key].price = resource.solo_price;
    manualSummaryItems[key].quantity = resource.quantity;
    manualSummaryItems[key].subtotal = resource.solo_price * resource.quantity;
    
    const priceInput = document.querySelector(`input.price-input[data-item="${key}"]`);
    const quantityInput = document.querySelector(`input.quantity-input[data-item="${key}"]`);
    if (priceInput) priceInput.value = resource.solo_price;
    if (quantityInput) quantityInput.value = resource.quantity;
}

function formatDateTime(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}`;
}

function updateCategoryFilterOptions() {
    const filterEl = document.getElementById('categoryFilter');
    if (!filterEl) return;
    
    const currentVal = filterEl.value;
    
    // 수집 대상: 전체 보기면 partsData, 템플릿 보기면 selectedParts
    let categories = new Set();
    
    if (partsViewMode === 'TEMPLATE') {
        selectedParts.forEach(item => {
            const major = item.part.major_category || item.part.category_major;
            if (major) categories.add(major);
        });
        // 인건비도 있다면 추가
        laborItems.forEach(item => {
             // 인건비는 보통 '인건비' 카테고리지만 필요하면 추가
        });
    } else {
        partsData.forEach(item => {
            const major = item.major_category || item.category_major;
            if (major) categories.add(major);
        });
    }
    
    // 기존 옵션 유지 (전체 카테고리)
    filterEl.innerHTML = '<option value="">전체 카테고리</option>';
    
    // 정렬 후 옵션 추가
    [...categories].sort().forEach(cat => {
        if (cat === '인건비' || cat === '전장/제어부 집계') return; // 필터에서 굳이 안 보여줘도 되는 것들 제외
        const option = document.createElement('option');
        option.value = cat;
        option.textContent = cat;
        filterEl.appendChild(option);
    });
    
    filterEl.value = currentVal; // 선택값 유지 시도
}

async function loadParts(highlightItemCode = null) {
    const loading = document.getElementById('loading');
    const tableContainer = document.getElementById('tableContainer');
    
    // [신규] 조회 모드에서는 검색 버튼이 '현재 목록 필터링' 역할만 수행
    if (pageMode === 'view') {
        renderTemplatePartsTable();
        return;
    }

    // 템플릿 보기에서는 API 재조회 대신, 템플릿(선택된 부품) 내에서만 필터링 후 테이블을 "통째로" 재렌더링
    if (partsViewMode === 'TEMPLATE') {
        if (loading) loading.style.display = 'none';
        renderTemplatePartsTable();
        return;
    }

    loading.style.display = 'block';
    tableContainer.innerHTML = '';
    
    const searchQuery = document.getElementById('searchInput').value;
    const category = document.getElementById('categoryFilter').value;
    
    let apiUrl = '/api/v1/parts?include_schema=true&limit=1000';
    if (searchQuery) apiUrl += `&name=${encodeURIComponent(searchQuery)}`;
    if (category) apiUrl += `&major=${encodeURIComponent(category)}`;
    
    try {
        const response = await fetch(apiUrl);
        if (!response.ok) throw new Error('API 호출 실패');
        const data = await response.json();
        
        const summaryCategories = ['전장/제어부 집계'];
        
        // [중요] 전체 데이터에서 수동 항목의 실제 ID(6글자)를 찾아서 매핑
        (data.items || []).forEach(item => {
            if (item.minor_category === 'Local 자재') {
                manualSummaryItems.LOCAL_MAT.id = item.id; // 예: "000008"
            }
            if (item.minor_category === '운영 PC/주액 PC') {
                manualSummaryItems.OPERATION_PC.id = item.id; // 예: "000009"
            }
            if (item.minor_category === '케이블 및 기타 잡자재') { // [신규]
                manualSummaryItems.CABLE_ETC.id = item.id;
            }
        });

        // 일반 부품 필터링
        const filteredItems = (data.items || []).filter(item => {
            const major = item.major_category || item.category_major || '';
            return !summaryCategories.includes(major) && major !== '인건비';
        });
        
        // 인건비 데이터 추출
        const laborMasterData = (data.items || []).filter(item => {
            return (item.major_category || item.category_major) === '인건비';
        }).sort((a, b) => b.item_code.localeCompare(a.item_code)); 

        if (laborItems.length === 0) {
            laborItems = laborMasterData.map(item => ({
                item_code: item.item_code, 
                id: item.id,             // [중요] 서버 전송용 6글자 ID
                name: item.minor_category || item.name, 
                unit: item.unit || 'M/D',
                price: item.solo_price || 0,
                quantity: 0,
                subtotal: 0,
                maker_id: item.maker_id,
                etc: null, // [신규] 인건비는 기타 비고 없음 강제
                ul: false,
                ce: false,
                kc: false
            }));
        }

        partsData = filteredItems;
        setPartsViewMode('ALL');
        renderTable(data.schema, filteredItems, highlightItemCode);
        renderLaborItems(); 
        updateCategoryFilterOptions(); // [신규] 카테고리 필터 옵션 갱신
        
    } catch (error) {
        console.error('Error:', error);
        tableContainer.innerHTML = `<div class="empty-state" style="color: #ef4444;">부품 목록 로드 실패: ${error.message}</div>`;
    } finally {
        loading.style.display = 'none';
    }
}

function renderTable(schema, items, highlightItemCode = null) {
    const tableContainer = document.getElementById('tableContainer');
    if (!items || items.length === 0) {
        tableContainer.innerHTML = '<div class="empty-state">부품이 없습니다</div>';
        return;
    }
    
    const isViewMode = pageMode === 'view';
    currentPartsDisplayOrder = [];
    
    const columns = [
        { key: 'major_category', title: 'Unit', width: '120px', align: 'center', sortable: false },
        { key: 'minor_category', title: '품목', width: '120px', align: 'left', sortable: true },
        { key: 'name', title: '모델명/규격', width: '200px', align: 'left', sortable: true },
        { key: 'maker_name', title: 'Maker', width: '100px', align: 'left', sortable: true },
        { key: 'ul', title: 'UL', width: '50px', align: 'center', sortable: false },
        { key: 'ce', title: 'CE', width: '50px', align: 'center', sortable: false },
        { key: 'kc', title: 'KC', width: '50px', align: 'center', sortable: false },
        { key: 'etc', title: '기타', width: '100px', align: 'center', sortable: false },
        { key: 'unit', title: '단위', width: '60px', align: 'center', sortable: false },
        { key: 'solo_price', title: '금액', width: '120px', align: 'right', sortable: true },
        { key: 'quantity', title: '수량', width: '100px', align: 'center', sortable: true },
        { key: 'subtotal', title: '합계 금액', width: '120px', align: 'right', sortable: false }
    ];
    
    let html = '<div class="table-container"><table class="data-table create-table" id="partsTable"><thead><tr>';
    columns.forEach(col => {
        const sortIcon = col.sortable && currentSortKey === col.key ? (currentSortOrder === 'asc' ? ' ▲' : ' ▼') : '';
        const onClick = col.sortable ? `onclick="sortTable('${col.key}')"` : '';
        html += `<th class="col-${col.align} ${col.sortable ? 'sortable' : ''}" style="width: ${col.width}" ${onClick}>${col.title}${sortIcon}</th>`;
    });
    html += '</tr></thead><tbody>';
    
    const majorKeyOf = (item) => (item.major_category || item.category_major || '기타');
    let displayItems = [...items];
    if (currentSortKey) {
        displayItems = sortItems(displayItems, currentSortKey, currentSortOrder);
    } else {
        // 정렬 키가 없을 때 기본 정렬: major_category -> item_code 순서
        displayItems.sort((a, b) => {
            const majorA = majorKeyOf(a);
            const majorB = majorKeyOf(b);
            if (majorA !== majorB) return majorA.localeCompare(majorB);
            const codeA = a.item_code || a.id || '';
            const codeB = b.item_code || b.id || '';
            return codeA.localeCompare(codeB);
        });
    }

    for (let rowIndex = 0; rowIndex < displayItems.length; rowIndex++) {
        const item = displayItems[rowIndex];
        const itemCode = item.item_code || item.id || '';
        const highlightClass = (highlightItemCode && itemCode === highlightItemCode) ? 'highlight-row' : '';

        if (itemCode) currentPartsDisplayOrder.push(itemCode);

        const majorKey = majorKeyOf(item);
        const isRunStart = rowIndex === 0 || majorKeyOf(displayItems[rowIndex - 1]) !== majorKey;
        const isRunEnd = rowIndex === displayItems.length - 1 || majorKeyOf(displayItems[rowIndex + 1]) !== majorKey;

        let rowSpan = 1;
        if (isRunStart) {
            while (rowIndex + rowSpan < displayItems.length && majorKeyOf(displayItems[rowIndex + rowSpan]) === majorKey) {
                rowSpan += 1;
            }
        }

        html += `<tr class="${isRunEnd ? 'category-last-row' : ''} ${highlightClass}" data-item-code="${itemCode}">`;

        columns.forEach(col => {
            let value = item[col.key] || item[col.key.replace('_', '')];
            const cellClass = `col-${col.align}`;

            if (col.key === 'major_category') {
                if (isRunStart) html += `<td class="${cellClass} category-cell" rowspan="${rowSpan}"><strong>${value || '-'}</strong></td>`;
                return;
            }

            html += `<td class="${cellClass}">`;
            if (col.key === 'quantity') {
                const currentQty = selectedParts.has(itemCode) ? selectedParts.get(itemCode).quantity : 0;
                if (isViewMode) html += `<span>${currentQty}</span>`;
                else html += `<input type="number" class="quantity-input" data-item-code="${itemCode}" min="0" value="${currentQty}" onchange="updateQuantity('${itemCode}', this.value)">`;
            } else if (col.key === 'subtotal') {
                const currentQty = selectedParts.has(itemCode) ? selectedParts.get(itemCode).quantity : 0;
                const currentPrice = selectedParts.has(itemCode) ? selectedParts.get(itemCode).solo_price : (item.solo_price || 0);
                html += `<span class="subtotal-value" data-item-code="${itemCode}">${(currentQty * currentPrice).toLocaleString('ko-KR')}</span>`;
            } else if (col.key === 'solo_price') {
                const currentPrice = selectedParts.has(itemCode) ? selectedParts.get(itemCode).solo_price : (item.solo_price || 0);
                if (isViewMode) html += `<span>${currentPrice.toLocaleString('ko-KR')}</span>`;
                else html += `<input type="number" class="price-input" data-item-code="${itemCode}" min="0" value="${currentPrice}" onchange="updatePrice('${itemCode}', this.value)">`;
            } else if (['ul', 'ce', 'kc'].includes(col.key)) {
                html += value ? '<span class="badge badge-success">O</span>' : '<span class="badge badge-default">-</span>';
            } else if (col.key === 'name') {
                html += `<div class="cell-wrapper">
                            <span>${value || '-'}</span>
                            <button class="hover-plus-btn" onclick="openCreatePopup('${item.item_code}'); event.stopPropagation();" title="이 정보로 신규 등록">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                                    <circle cx="12" cy="12" r="10"></circle>
                                    <line x1="12" y1="8" x2="12" y2="16"></line>
                                    <line x1="8" y1="12" x2="16" y2="12"></line>
                                </svg>
                            </button>
                         </div>`;
            } else {
                html += value || '-';
            }
            html += '</td>';
        });

        html += '</tr>';
    }
    html += '</tbody></table></div>';
    tableContainer.innerHTML = html;
}

function renderLaborItems() {
    const summaryTableBody = document.getElementById('summaryTableBody');
    const laborTotalRow = document.getElementById('laborRowsPlaceholder');
    
    const existingRows = summaryTableBody.querySelectorAll('.labor-fixed-row');
    existingRows.forEach(row => row.remove());
    
    if (laborItems.length === 0) return;

    // [신규] 뷰 모드에 따른 필터링
    let displayItems = laborItems;
    if (partsViewMode === 'TEMPLATE') {
        // 템플릿에 포함된 항목이거나, 수량이 0보다 큰(사용자가 추가한) 항목만 표시
        displayItems = laborItems.filter(item => item.isTemplate || item.quantity > 0);
    }
    
    if (displayItems.length === 0) return; // 표시할 항목이 없으면 중단
    
    const isViewMode = pageMode === 'view';
    const fragment = document.createDocumentFragment();
    
    displayItems.forEach((item, index) => {
        const tr = document.createElement('tr');
        tr.className = 'labor-fixed-row';
        tr.setAttribute('data-item-code', item.item_code);
        
        let html = '';
        
        if (index === 0) {
            html += `<td class="col-center category-cell labor-header-cell" rowspan="${displayItems.length}">
                <strong>인건비</strong>
            </td>`;
        }
        
        html += `<td class="col-left">${item.name}</td>`;
        html += `<td class="col-left">-</td>`;
        html += `<td class="col-left">-</td>`;
        html += `<td class="col-center"><span class="badge-gray-box"></span></td>`;
        html += `<td class="col-center"><span class="badge-gray-box"></span></td>`;
        html += `<td class="col-center"><span class="badge-gray-box"></span></td>`;
        html += `<td class="col-center">-</td>`;
        html += `<td class="col-center">${item.unit}</td>`;
        
        if (isViewMode) {
            html += `<td class="col-right">${item.price.toLocaleString('ko-KR')}</td>`;
        } else {
            html += `<td class="col-right">
                <input type="number" class="price-input" value="${item.price}" min="0"
                    onchange="updateLaborItem('${item.item_code}', 'price', this.value)">
            </td>`;
        }
        
        if (isViewMode) {
            html += `<td class="col-center">${item.quantity}</td>`;
        } else {
            html += `<td class="col-center">
                <input type="number" class="quantity-input" value="${item.quantity}" min="0"
                    onchange="updateLaborItem('${item.item_code}', 'quantity', this.value)">
            </td>`;
        }
        
        html += `<td class="col-right labor-subtotal"><strong>${item.subtotal.toLocaleString('ko-KR')}</strong></td>`;
        
        tr.innerHTML = html;
        fragment.appendChild(tr);
    });
    
    summaryTableBody.insertBefore(fragment, laborTotalRow);
}

function updateLaborItem(itemCode, field, value) {
    const item = laborItems.find(i => i.item_code === itemCode);
    if (!item) return;
    
    const numValue = parseInt(value) || 0;
    item[field] = numValue;
    item.subtotal = item.price * item.quantity;
    
    const row = document.querySelector(`.labor-fixed-row[data-item-code="${itemCode}"]`);
    if (row) {
        const subtotalCell = row.querySelector('.labor-subtotal strong');
        if (subtotalCell) subtotalCell.textContent = item.subtotal.toLocaleString('ko-KR');
    }
    
    updateSummary();
    markAsDirty(); // [신규] 변경 감지
}

function sortItems(items, key, order) {
    return items.sort((a, b) => {
        let aVal = a[key], bVal = b[key];
        if (key === 'solo_price' || key === 'quantity') {
            aVal = parseFloat(aVal) || 0; bVal = parseFloat(bVal) || 0;
        } else {
            aVal = (aVal || '').toString().toLowerCase(); bVal = (bVal || '').toString().toLowerCase();
        }
        if (aVal < bVal) return order === 'asc' ? -1 : 1;
        if (aVal > bVal) return order === 'asc' ? 1 : -1;
        return 0;
    });
}

function sortTable(key) {
    if (currentSortKey === key) currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
    else { currentSortKey = key; currentSortOrder = 'asc'; }
    renderTable(null, partsData);
}

function updatePrice(itemCode, newPrice) {
    const price = parseInt(newPrice) || 0;
    const part = partsData.find(p => (p.item_code || p.id) === itemCode);
    if (part) {
        part.solo_price = price;
    }
    if (selectedParts.has(itemCode)) {
        const selected = selectedParts.get(itemCode);
        selected.solo_price = price;
        selected.subtotal = selected.quantity * price;
        selectedParts.set(itemCode, selected);
    }

    // 현재 화면에 입력이 있으면 동기화
    document.querySelectorAll(`.price-input[data-item-code="${itemCode}"]`).forEach(el => {
        el.value = price;
    });

    updateSubtotal(itemCode);
    if (partsViewMode === 'TEMPLATE') renderTemplatePartsTable();
    updateSummary();
    markAsDirty(); // [신규] 변경 감지
}

function updateQuantity(itemCode, quantity) {
    const qty = parseInt(quantity) || 0;
    if (qty > 0) {
        const alreadySelected = selectedParts.has(itemCode);
        const part = partsData.find(p => (p.item_code || p.id) === itemCode) || (alreadySelected ? selectedParts.get(itemCode).part : null);
        if (part) {
            const currentPrice = alreadySelected ? selectedParts.get(itemCode).solo_price : (part.solo_price || 0);
            selectedParts.set(itemCode, { part: part, quantity: qty, solo_price: currentPrice, subtotal: qty * currentPrice });
            if (!alreadySelected) {
                addToSelectedOrder(itemCode);
            }
        }
    } else {
        selectedParts.delete(itemCode);
        removeFromSelectedOrder(itemCode);
    }

    // 현재 화면에 입력이 있으면 동기화
    document.querySelectorAll(`.quantity-input[data-item-code="${itemCode}"]`).forEach(el => {
        el.value = qty;
    });

    updateSubtotal(itemCode);
    if (partsViewMode === 'TEMPLATE') renderTemplatePartsTable();
    updateSummary();
    markAsDirty(); // [신규] 변경 감지
}

function addToSelectedOrder(itemCode) {
    if (selectedOrder.includes(itemCode)) return;

    if (pendingInsertIndex === null || pendingInsertIndex === undefined) {
        const newDisplayIndex = currentPartsDisplayOrder.indexOf(itemCode);
        if (newDisplayIndex < 0 || currentPartsDisplayOrder.length === 0) {
            selectedOrder.push(itemCode);
            return;
        }

        let insertAt = selectedOrder.length;
        for (let i = 0; i < selectedOrder.length; i++) {
            const existingDisplayIndex = currentPartsDisplayOrder.indexOf(selectedOrder[i]);
            if (existingDisplayIndex < 0) continue;
            if (existingDisplayIndex > newDisplayIndex) {
                insertAt = i;
                break;
            }
        }

        selectedOrder.splice(insertAt, 0, itemCode);
        return;
    }

    const index = Math.max(0, Math.min(pendingInsertIndex, selectedOrder.length));
    selectedOrder.splice(index, 0, itemCode);
    pendingInsertIndex = null;
    updateInsertStatus();
}

function removeFromSelectedOrder(itemCode) {
    const index = selectedOrder.indexOf(itemCode);
    if (index >= 0) selectedOrder.splice(index, 1);

    if (pendingInsertIndex !== null && pendingInsertIndex > selectedOrder.length) {
        pendingInsertIndex = null;
        updateInsertStatus();
    }
}

function setInsertAfter(itemCode) {
    if (pageMode === 'view') return;
    const index = selectedOrder.indexOf(itemCode);
    pendingInsertIndex = index >= 0 ? index + 1 : selectedOrder.length;
    updateInsertStatus();
}

function clearInsertMode() {
    pendingInsertIndex = null;
    updateInsertStatus();
}

function updateInsertStatus() {
    const el = document.getElementById('insertStatus');
    const cancelBtn = document.getElementById('cancelInsertBtn');
    if (!el) return;
    if (pendingInsertIndex === null) {
        el.textContent = '';
        if (cancelBtn) cancelBtn.style.display = 'none';
        return;
    }
    el.textContent = `삽입 위치 지정됨: 다음으로 선택하는 부품이 ${pendingInsertIndex + 1}번째로 들어갑니다.`;
    if (cancelBtn) cancelBtn.style.display = '';
}

function moveSelected(itemCode, direction) {
    if (pageMode === 'view') return;
    const index = selectedOrder.indexOf(itemCode);
    if (index < 0) return;

    const target = index + direction;
    if (target < 0 || target >= selectedOrder.length) return;

    const tmp = selectedOrder[index];
    selectedOrder[index] = selectedOrder[target];
    selectedOrder[target] = tmp;

    renderTemplatePartsTable();
    markAsDirty();
}

function removeSelectedItem(itemCode) {
    if (pageMode === 'view') return;
    selectedParts.delete(itemCode);
    removeFromSelectedOrder(itemCode);

    document.querySelectorAll(`.quantity-input[data-item-code="${itemCode}"]`).forEach(el => {
        el.value = 0;
    });

    updateSubtotal(itemCode);
    renderTemplatePartsTable();
    updateSummary();
    markAsDirty();
}

function renderSelectedOrderTable() {
    renderTemplatePartsTable();
}

function renderTemplatePartsTable() {
    const tableContainer = document.getElementById('tableContainer');
    if (!tableContainer) return;

    if (selectedOrder.length === 0) {
        tableContainer.innerHTML = '<div class="empty-state">템플릿에 선택된 부품이 없습니다</div>';
        setPartsViewMode('ALL');
        return;
    }

    const isViewMode = pageMode === 'view';
    currentPartsDisplayOrder = [];

    const searchQuery = (document.getElementById('searchInput')?.value || '').trim().toLowerCase();
    const category = (document.getElementById('categoryFilter')?.value || '').trim();

    const rows = [];
    selectedOrder.forEach((itemCode, index) => {
        const selected = selectedParts.get(itemCode);
        if (!selected) return;
        const part = selected.part || {};
        const major = part.major_category || part.category_major || '기타';
        const minor = part.minor_category || part.category_minor || '-';
        const name = part.model_name || part.name || '-';
        const maker = part.maker_name || '-';

        if (searchQuery) {
            const hay = `${major} ${minor} ${name} ${maker}`.toLowerCase();
            if (!hay.includes(searchQuery)) return;
        }
        if (category) {
            if (!major.includes(category)) return;
        }

        currentPartsDisplayOrder.push(itemCode);
        rows.push({
            itemCode,
            index,
            major,
            minor,
            name,
            maker,
            ul: !!part.ul,
            ce: !!part.ce,
            kc: !!part.kc,
            etc: part.etc || part.certification_etc || '-',
            unit: part.unit || '-',
            solo_price: selected.solo_price || 0,
            quantity: selected.quantity || 0,
        });
    });

    if (rows.length === 0) {
        tableContainer.innerHTML = '<div class="empty-state">검색 결과가 없습니다</div>';
        return;
    }

    let html = '<div class="table-container"><table class="data-table create-table" id="templateTable"><thead><tr>';
    html += '<th class="col-center" style="width: 120px">Unit</th>';
    html += '<th class="col-left" style="width: 120px">품목</th>';
    html += '<th class="col-left" style="width: 200px">모델명/규격</th>';
    html += '<th class="col-left" style="width: 100px">Maker</th>';
    html += '<th class="col-center" style="width: 50px">UL</th>';
    html += '<th class="col-center" style="width: 50px">CE</th>';
    html += '<th class="col-center" style="width: 50px">KC</th>';
    html += '<th class="col-center" style="width: 100px">기타</th>';
    html += '<th class="col-center" style="width: 60px">단위</th>';
    html += '<th class="col-right" style="width: 120px">금액</th>';
    html += '<th class="col-center" style="width: 100px">수량</th>';
    html += '<th class="col-right" style="width: 120px">합계 금액</th>';
    html += '<th class="col-center" style="width: 170px">조작</th>';
    html += '</tr></thead><tbody>';

    const majorKeyOf = (r) => (r.major || '').toString();
    for (let rowIndex = 0; rowIndex < rows.length; rowIndex++) {
        const r = rows[rowIndex];
        const majorKey = majorKeyOf(r);
        const isRunStart = rowIndex === 0 || majorKeyOf(rows[rowIndex - 1]) !== majorKey;
        const isRunEnd = rowIndex === rows.length - 1 || majorKeyOf(rows[rowIndex + 1]) !== majorKey;
        let rowSpan = 1;
        if (isRunStart) {
            while (rowIndex + rowSpan < rows.length && majorKeyOf(rows[rowIndex + rowSpan]) === majorKey) {
                rowSpan += 1;
            }
        }

        const subtotal = (r.solo_price * r.quantity) || 0;
        html += `<tr class="${isRunEnd ? 'category-last-row' : ''}" data-item-code="${r.itemCode}">`;
        if (isRunStart) html += `<td class="col-center category-cell" rowspan="${rowSpan}"><strong>${r.major || '-'}</strong></td>`;
        html += `<td class="col-left">${r.minor || '-'}</td>`;
        html += `<td class="col-left"><div class="cell-wrapper">
                    <span>${r.name || '-'}</span>
                    <button class="hover-plus-btn" onclick="openCreatePopup('${r.itemCode}'); event.stopPropagation();" title="이 정보로 신규 등록">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                            <circle cx="12" cy="12" r="10"></circle>
                            <line x1="12" y1="8" x2="12" y2="16"></line>
                            <line x1="8" y1="12" x2="16" y2="12"></line>
                        </svg>
                    </button>
                </div></td>`;
        html += `<td class="col-left">${r.maker || '-'}</td>`;
        html += `<td class="col-center">${r.ul ? '<span class="badge badge-success">O</span>' : '<span class="badge badge-default">-</span>'}</td>`;
        html += `<td class="col-center">${r.ce ? '<span class="badge badge-success">O</span>' : '<span class="badge badge-default">-</span>'}</td>`;
        html += `<td class="col-center">${r.kc ? '<span class="badge badge-success">O</span>' : '<span class="badge badge-default">-</span>'}</td>`;
        html += `<td class="col-center">${r.etc || '-'}</td>`;
        html += `<td class="col-center">${r.unit || '-'}</td>`;

        if (isViewMode) {
            html += `<td class="col-right">${(r.solo_price || 0).toLocaleString('ko-KR')}</td>`;
            html += `<td class="col-center">${r.quantity || 0}</td>`;
        } else {
            html += `<td class="col-right"><input type="number" class="price-input" data-item-code="${r.itemCode}" min="0" value="${r.solo_price || 0}" onchange="updatePrice('${r.itemCode}', this.value)"></td>`;
            html += `<td class="col-center"><input type="number" class="quantity-input" data-item-code="${r.itemCode}" min="0" value="${r.quantity || 0}" onchange="updateQuantity('${r.itemCode}', this.value)"></td>`;
        }

        html += `<td class="col-right"><strong class="subtotal-value" data-item-code="${r.itemCode}">${subtotal.toLocaleString('ko-KR')}</strong></td>`;

        html += '<td class="col-center">';
        if (isViewMode) {
            html += '<span class="text-muted">-</span>';
        } else {
            html += `<button class="btn btn-secondary btn-xs" onclick="moveSelected('${r.itemCode}', -1)" title="위로">↑</button>`;
            html += `<button class="btn btn-secondary btn-xs" onclick="moveSelected('${r.itemCode}', 1)" title="아래로">↓</button>`;
            html += `<button class="btn btn-primary btn-xs" onclick="setInsertAfter('${r.itemCode}')" title="이 아래에 삽입">+</button>`;
            html += `<button class="btn btn-danger btn-xs" onclick="removeSelectedItem('${r.itemCode}')" title="삭제">×</button>`;
        }
        html += '</td>';

        html += '</tr>';
    }

    html += '</tbody></table></div>';
    tableContainer.innerHTML = html;
}

function updateSubtotal(itemCode) {
    const qty = selectedParts.has(itemCode) ? selectedParts.get(itemCode).quantity : 0;
    const price = selectedParts.has(itemCode) ? selectedParts.get(itemCode).solo_price : (partsData.find(p => (p.item_code || p.id) === itemCode)?.solo_price || 0);
    document.querySelectorAll(`.subtotal-value[data-item-code="${itemCode}"]`).forEach(el => {
        el.textContent = (qty * price).toLocaleString('ko-KR');
    });
}

function updateSummary() {
    const categoryOrder = ['전장 판넬 판금 및 명판', '판넬 차단기류', 'PLC Set', 'Touch Screen', '판넬 주요자재', '판넬 기타자재', '케이블 및 기타 잡자재'];
    const categoryTotals = {};
    categoryOrder.forEach(cat => categoryTotals[cat] = 0);
    
    selectedParts.forEach(item => {
        const major = item.part.major_category || item.part.category_major || '기타';
        if (categoryTotals[major] !== undefined) categoryTotals[major] += item.subtotal;
    });
    
    categoryOrder.forEach(cat => {
        const row = document.querySelector(`#summaryTable tr[data-category="${cat}"]`);
        if (row) row.querySelector('.summary-amount').textContent = categoryTotals[cat].toLocaleString('ko-KR');
    });
    
    let materialTotal = 0;
    selectedParts.forEach(item => materialTotal += item.subtotal);
    Object.keys(manualSummaryItems).forEach(key => materialTotal += manualSummaryItems[key].subtotal);
    document.getElementById('materialTotalAmount').textContent = materialTotal.toLocaleString('ko-KR');
    
    let laborTotal = 0;
    laborItems.forEach(item => laborTotal += item.subtotal);
    document.getElementById('laborTotalAmount').textContent = laborTotal.toLocaleString('ko-KR');
    
    const grandTotal = materialTotal + laborTotal;
    document.getElementById('grandTotalAmount').textContent = grandTotal.toLocaleString('ko-KR');
    document.getElementById('totalPrice').value = grandTotal.toLocaleString('ko-KR') + '원';
}

function updateManualSummary(itemKey, field, value) {
    if (pageMode === 'view') return;
    const numValue = parseInt(value) || 0;
    manualSummaryItems[itemKey][field] = numValue;
    manualSummaryItems[itemKey].subtotal = manualSummaryItems[itemKey].price * manualSummaryItems[itemKey].quantity;
    
    const row = document.querySelector(`#summaryTable tr[data-item="${itemKey}"]`);
    if (row) row.querySelector('.summary-amount').textContent = manualSummaryItems[itemKey].subtotal.toLocaleString('ko-KR');
    updateSummary();
    markAsDirty(); // [신규] 변경 감지
}

function handleSearch(event) {
    if (event.key !== 'Enter') return;
    if (partsViewMode === 'TEMPLATE') renderTemplatePartsTable();
    else loadParts();
}

// [수정] submitMachine 함수: 수동 항목과 인건비 항목의 ID를 올바르게 전송
async function submitMachine() {
    const machineName = document.getElementById('machineName').value.trim();
    const creator = document.getElementById('creator').value.trim();
    if (!machineName) return alert('장비명을 입력하세요.');
    if (!creator) return alert('작성자명을 입력하세요.');

    if (selectedParts.size === 0 && laborItems.every(i => i.quantity === 0)) {
        return alert('최소 1개 이상의 부품 또는 인건비 항목을 입력하세요.');
    }

    const resources = [];
    selectedOrder.forEach(itemCode => {
        const item = selectedParts.get(itemCode);
        if (!item) return;
        const part = item.part || {};

        // 필수 필드 검증
        if (!part.maker_id || !part.id) {
            console.error('Invalid part data:', { itemCode, part });
            return;
        }

        resources.push({
            maker_id: part.maker_id,
            resources_id: part.id,
            solo_price: item.solo_price,
            quantity: item.quantity,
            display_major: part.category_major || part.major_category || null,
            display_minor: part.category_minor || part.minor_category || null,
            display_model_name: part.model_name || part.name || null,
            display_maker_name: part.maker_name || null,
            display_unit: part.unit || null,
        });
    });
    
    // [수정] 수동 항목: loadParts에서 찾은 실제 ID 사용
    Object.keys(manualSummaryItems).forEach(key => {
        const item = manualSummaryItems[key];
        if (item.quantity > 0) {
            let resourceId = item.id;
            let displayName = '';
            
            if (!resourceId) {
                if (key === 'LOCAL_MAT') {
                    resourceId = '000008';
                    displayName = 'Local 자재';
                } else if (key === 'OPERATION_PC') {
                    resourceId = '000009';
                    displayName = '운영 PC/주액 PC';
                } else if (key === 'CABLE_ETC') {
                    resourceId = '000007';
                    displayName = '케이블 및 기타 잡자재';
                }
            } else {
                if (key === 'LOCAL_MAT') displayName = 'Local 자재';
                else if (key === 'OPERATION_PC') displayName = '운영 PC/주액 PC';
                else if (key === 'CABLE_ETC') displayName = '케이블 및 기타 잡자재';
            }

            resources.push({ 
                maker_id: "T000", 
                resources_id: resourceId, 
                solo_price: item.price, 
                quantity: item.quantity,
                // ✅ 아래 5개 필드 추가!
                display_major: "전장/제어부 집계",
                display_minor: displayName,
                display_model_name: "-",
                display_maker_name: "T000",
                display_unit: "ea"
            });
        }
    });
    
    // [수정] 인건비 항목: item.id (6글자) 사용
    laborItems.forEach(item => {
        if (item.quantity > 0) {
            resources.push({ 
                maker_id: item.maker_id || "T000", 
                resources_id: item.id, // [중요] item.item_code(11자) 대신 item.id(6자) 사용
                solo_price: item.price, 
                quantity: item.quantity 
            });
        }
    });
    
    const requestData = {
        name: machineName,
        manufacturer: document.getElementById('manufacturer').value.trim() || null,
        client: document.getElementById('client').value.trim() || null,
        creator: creator,
        description: document.getElementById('description').value.trim() || null,
        resources: resources
    };
    
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true; submitBtn.textContent = '등록 중...';
    
    try {
        const response = await fetch('/api/v1/quotation/machine', {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(requestData)
        });

        if (response.ok) {
            const data = await response.json();
            alert(`장비 견적서가 등록되었습니다!\nID: ${data.id}`);
            window.location.href = `/service/quotation/machine/${data.id}`;
        } else {
            // 에러 응답 처리 - Content-Type에 따라 JSON 또는 텍스트로 처리
            let errorMessage = '';
            const contentType = response.headers.get('content-type');

            try {
                if (contentType && contentType.includes('application/json')) {
                    const error = await response.json();
                    console.error('Submit Error (JSON):', error);
                    errorMessage = JSON.stringify(error.detail || error, null, 2);
                } else {
                    const errorText = await response.text();
                    console.error('Submit Error (Text):', errorText);
                    errorMessage = `서버 오류 (${response.status}):\n${errorText.substring(0, 500)}`;
                }
            } catch (e) {
                console.error('Error parsing response:', e);
                errorMessage = `응답 파싱 실패 (${response.status})`;
            }

            alert('등록 실패:\n' + errorMessage);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('등록 중 오류가 발생했습니다.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = '등록완료';
    }
}

// [수정] updateMachine 함수도 동일하게 ID 사용하도록 수정
async function updateMachine() {
    const machineName = document.getElementById('machineName').value.trim();
    if (!machineName) return alert('장비명을 입력하세요.');

    if (selectedParts.size === 0 && laborItems.every(i => i.quantity === 0)) {
        return alert('최소 1개 이상의 부품 또는 인건비 항목을 입력하세요.');
    }

    const resources = [];
    selectedOrder.forEach(itemCode => {
        const item = selectedParts.get(itemCode);
        if (!item) return;
        const part = item.part || {};

        // 필수 필드 검증
        if (!part.maker_id || !part.id) {
            console.error('Invalid part data:', { itemCode, part });
            return;
        }

        resources.push({
            maker_id: part.maker_id,
            resources_id: part.id,
            solo_price: item.solo_price,
            quantity: item.quantity,
            display_major: part.category_major || part.major_category || null,
            display_minor: part.category_minor || part.minor_category || null,
            display_model_name: part.model_name || part.name || null,
            display_maker_name: part.maker_name || null,
            display_unit: part.unit || null,
        });
    });
    
    Object.keys(manualSummaryItems).forEach(key => {
        const item = manualSummaryItems[key];
        if (item.quantity > 0) {
            // 💡 [수정] T000의 resources_id를 명시적으로 처리
            let resourceId = item.id;
            
            if (!resourceId) {
                if (key === 'LOCAL_MAT') {
                    resourceId = '000008';
                } else if (key === 'OPERATION_PC') {
                    resourceId = '000009';
                } else if (key === 'CABLE_ETC') { // 💡 CABLE_ETC에 대한 명시적 폴백 (T000-000007)
                    resourceId = '000007';
                } else {
                    resourceId = '000000'; // 최종 폴백
                }
            }

            resources.push({ maker_id: "T000", resources_id: resourceId, solo_price: item.price, quantity: item.quantity });
        }
    });
    
    laborItems.forEach(item => {
        if (item.quantity > 0) {
            resources.push({ 
                maker_id: item.maker_id || "T000", 
                resources_id: item.id,
                solo_price: item.price, 
                quantity: item.quantity,
                display_major: "인건비",
                display_minor: item.name || "계약 실계",
                display_model_name: "-",
                display_maker_name: "T000",
                display_unit: item.unit || "M/D"
            });
        }
    });
    
    const requestData = {
        name: machineName,
        manufacturer: document.getElementById('manufacturer').value.trim() || null,
        client: document.getElementById('client').value.trim() || null,
        description: document.getElementById('description').value.trim() || null,
        resources: resources
    };
    
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true; submitBtn.textContent = '수정 중...';
    
    try {
        const response = await fetch(`/api/v1/quotation/machine/${machineId}`, {
            method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(requestData)
        });

        if (response.ok) {
            alert('장비 견적서가 수정되었습니다!');
            window.location.href = `?mode=view&id=${machineId}`;
        } else {
            // 에러 응답 처리 - Content-Type에 따라 JSON 또는 텍스트로 처리
            let errorMessage = '';
            const contentType = response.headers.get('content-type');

            try {
                if (contentType && contentType.includes('application/json')) {
                    const error = await response.json();
                    console.error('Update Error (JSON):', error);
                    errorMessage = JSON.stringify(error.detail || error, null, 2);
                } else {
                    const errorText = await response.text();
                    console.error('Update Error (Text):', errorText);
                    errorMessage = `서버 오류 (${response.status}):\n${errorText.substring(0, 500)}`;
                }
            } catch (e) {
                console.error('Error parsing response:', e);
                errorMessage = `응답 파싱 실패 (${response.status})`;
            }

            alert('수정 실패:\n' + errorMessage);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('수정 중 오류가 발생했습니다.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = '수정완료';
    }
}

// [수정] 임시 저장 기능 (Silent 모드 지원)
async function saveDraft(isSilent = false) {
    const machineName = document.getElementById('machineName').value.trim();
    const creator = document.getElementById('creator').value.trim();

    // Silent 모드일 때는 필수값 없으면 조용히 리턴
    if (isSilent && (!machineName || !creator)) return;

    if (!machineName) return alert('장비명을 입력하세요.');
    if (!creator) return alert('작성자명을 입력하세요.');

    // 이미 저장 중이면 중복 실행 방지
    if (isSaving) {
        console.log('이미 저장 중입니다. 요청 무시.');
        return;
    }

    // 상태 표시
    const statusEl = document.getElementById('autoSaveStatus');
    if (isSilent && statusEl) statusEl.textContent = '자동 저장 중...';

    isSaving = true; // 저장 시작

    // 데이터 수집 로직 (submitMachine과 동일)
    const resources = [];
    selectedOrder.forEach(itemCode => {
        const item = selectedParts.get(itemCode);
        if (!item) return;
        const part = item.part || {};

        // 필수 필드 검증
        if (!part.maker_id || !part.id) {
            console.error('Invalid part data:', { itemCode, part });
            return;
        }

        resources.push({
            maker_id: part.maker_id,
            resources_id: part.id,
            solo_price: item.solo_price,
            quantity: item.quantity,
            display_major: part.category_major || part.major_category || null,
            display_minor: part.category_minor || part.minor_category || null,
            display_model_name: part.model_name || part.name || null,
            display_maker_name: part.maker_name || null,
            display_unit: part.unit || null,
        });
    });
    
    Object.keys(manualSummaryItems).forEach(key => {
        const item = manualSummaryItems[key];
        if (item.quantity > 0) {
            // 💡 [수정] T000의 resources_id를 명시적으로 처리
            let resourceId = item.id;
            
            if (!resourceId) {
                if (key === 'LOCAL_MAT') {
                    resourceId = '000008';
                } else if (key === 'OPERATION_PC') {
                    resourceId = '000009';
                } else if (key === 'CABLE_ETC') { // 💡 CABLE_ETC에 대한 명시적 폴백 (T000-000007)
                    resourceId = '000007';
                } else {
                    resourceId = '000000'; // 최종 폴백
                }
            }

            resources.push({ maker_id: "T000", resources_id: resourceId, solo_price: item.price, quantity: item.quantity });
        }
    });
    
    laborItems.forEach(item => {
        if (item.quantity > 0) {
            resources.push({ 
                maker_id: item.maker_id || "T000", 
                resources_id: item.id,
                solo_price: item.price, 
                quantity: item.quantity,
                // ✅ 추가!
                display_major: "인건비",
                display_minor: item.name || "계약 실계",
                display_model_name: "-",
                display_maker_name: "T000",
                display_unit: item.unit || "M/D"
            });
        }
    });
    
    const requestData = {
        name: machineName,
        manufacturer: document.getElementById('manufacturer').value.trim() || null,
        client: document.getElementById('client').value.trim() || null,
        creator: creator,
        description: document.getElementById('description').value.trim() || null,
        resources: resources
    };

    // 저장 로직 (POST 또는 PUT)
    try {
        let response;
        if (!machineId) {
            // 신규 등록 (POST)
            response = await fetch('/api/v1/quotation/machine', {
                method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(requestData)
            });
        } else {
            // 수정 (PUT)
            response = await fetch(`/api/v1/quotation/machine/${machineId}`, {
                method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(requestData)
            });
        }

        if (response.ok) {
            const data = await response.json();
            
            // 신규 등록이었다면 ID 설정 및 URL 변경 (페이지 이동 없음)
            if (!machineId) {
                machineId = data.id;
                pageMode = 'edit';
                const newUrl = `${window.location.pathname}?mode=edit&id=${machineId}`;
                window.history.replaceState({ path: newUrl }, '', newUrl);
                
                document.querySelector('.create-header h2').textContent = '장비 견적서 수정'; // h2 내용만 변경 (span 유지)
                document.getElementById('submitBtn').textContent = '수정완료';
                document.getElementById('submitBtn').onclick = updateMachine;
                document.querySelector('.action-footer .btn-secondary').textContent = '취소';
            }
            
            // [중요] 저장 성공 시 Dirty 플래그 해제 및 시간 표시
            isDirty = false;
            const time = new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
            if (statusEl) {
                statusEl.textContent = `마지막 저장: ${time}`;
                statusEl.style.color = '#10b981'; // 초록색
            }

            if (!isSilent) alert('임시 저장되었습니다.');
        } else {
            // 에러 응답 처리 - Content-Type에 따라 JSON 또는 텍스트로 처리
            let errorMessage = '';
            const contentType = response.headers.get('content-type');

            try {
                if (contentType && contentType.includes('application/json')) {
                    const error = await response.json();
                    console.error('Save Draft Error (JSON):', error);
                    errorMessage = JSON.stringify(error.detail || error, null, 2);
                } else {
                    const errorText = await response.text();
                    console.error('Save Draft Error (Text):', errorText);
                    errorMessage = `서버 오류 (${response.status}): ${errorText.substring(0, 200)}`;
                }
            } catch (e) {
                console.error('Error parsing response:', e);
                errorMessage = `응답 파싱 실패 (${response.status})`;
            }

            if (statusEl) {
                statusEl.textContent = '자동 저장 실패';
                statusEl.style.color = '#ef4444';
            }
            if (!isSilent) alert('임시 저장 실패:\n' + errorMessage);
        }
    } catch (error) {
        console.error('Error:', error);
        if (statusEl) {
            statusEl.textContent = '저장 오류 발생';
            statusEl.style.color = '#ef4444';
        }
        if (!isSilent) alert('저장 중 오류가 발생했습니다.');
    } finally {
        isSaving = false; // 저장 완료 (성공/실패 무관)
    }
}