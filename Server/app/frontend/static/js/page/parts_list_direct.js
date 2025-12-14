let currentSkip = 0;
let currentLimit = 30; // 한 번에 30개씩
let totalItems = 0;
let isLoading = false;
let hasMore = true;
let observer;

// 페이지 로드 시
document.addEventListener('DOMContentLoaded', function() {
    initObserver();
    loadData(true);
});

// 무한 스크롤 옵저버 초기화
function initObserver() {
    const sentinel = document.getElementById('scrollSentinel');
    
    // 기존 observer 해제
    if (observer) observer.disconnect();

    observer = new IntersectionObserver((entries) => {
        // 화면에 들어왔고, 로딩 중이 아니고, 데이터가 더 있다면 로드
        if (entries[0].isIntersecting && !isLoading && hasMore) {
            loadData(false);
        }
    }, { threshold: 0.1 });
    
    if (sentinel) observer.observe(sentinel);
}

// 데이터 로드
async function loadData(isInitial = false) {
    if (isLoading) return;
    isLoading = true;
    
    const loadingEl = document.getElementById('loading');
    const sentinel = document.getElementById('scrollSentinel');
    const tableContainer = document.getElementById('tableContainer');
    
    if (isInitial) {
        currentSkip = 0;
        hasMore = true;
        totalItems = 0;
        if (tableContainer) tableContainer.innerHTML = '';
        if (loadingEl) loadingEl.style.display = 'block';
        if (sentinel) sentinel.style.display = 'none';
    } else {
        if (sentinel) {
            sentinel.style.display = 'block';
            sentinel.innerHTML = '<span class="loading-text">더 불러오는 중...</span>';
        }
    }
    
    const searchQuery = document.getElementById('searchInput').value;
    const category = document.getElementById('categoryFilter').value;
    
    let apiUrl = '/api/v1/parts?include_schema=true';
    apiUrl += `&skip=${currentSkip}&limit=${currentLimit}`;
    
    if (searchQuery) apiUrl += `&name=${encodeURIComponent(searchQuery)}`;
    if (category) apiUrl += `&major=${encodeURIComponent(category)}`;
    
    try {
        const response = await fetch(apiUrl);
        if (!response.ok) throw new Error('API 호출 실패');
        
        const data = await response.json();
        const newItems = data.items || [];
        totalItems = data.total || 0;
        
        // 더 가져올 데이터가 없으면 hasMore = false
        if (newItems.length < currentLimit || (currentSkip + newItems.length >= totalItems)) {
            hasMore = false;
        }
        
        renderTable(data.schema, newItems, isInitial);
        
        currentSkip += newItems.length;
        
    } catch (error) {
        console.error('Error:', error);
        if (isInitial && tableContainer) {
            tableContainer.innerHTML = `<div class="empty-state" style="color: #ef4444;">데이터 로드 실패: ${error.message}</div>`;
        }
    } finally {
        isLoading = false;
        if (loadingEl) loadingEl.style.display = 'none';
        
        if (sentinel) {
            if (hasMore) {
                sentinel.style.display = 'block';
                sentinel.innerHTML = ''; // 감지용 빈 공간 유지
            } else {
                sentinel.style.display = 'none';
            }
        }
    }
}

// 테이블 렌더링 (Append 방식)
function renderTable(schema, items, isInitial) {
    const tableContainer = document.getElementById('tableContainer');
    
    if (isInitial && items.length === 0) {
        tableContainer.innerHTML = '<div class="empty-state">데이터가 없습니다</div>';
        return;
    }
    
    let tableBody = tableContainer.querySelector('tbody');
    
    // 테이블 생성 (첫 로딩이거나 테이블이 없을 때)
    if (!tableBody || isInitial) {
        let totalRatio = 0;
        for (const key in schema) totalRatio += schema[key].ratio || 1;
        
        let html = '<div class="table-container"><table class="data-table" id="partsTable">';
        html += '<thead><tr>';
        html += '<th class="col-center" style="width: 50px"><input type="checkbox" id="checkAll" onchange="toggleAllRows()"></th>';
        
        for (const key in schema) {
            const col = schema[key];
            const width = ((col.ratio || 1) / totalRatio * 100).toFixed(1);
            const align = col.align || (col.type === 'integer' ? 'right' : (col.type === 'boolean' ? 'center' : 'left'));
            html += `<th class="col-${align}" style="width: ${width}%">${col.title}</th>`;
        }
        html += '</tr></thead><tbody></tbody></table></div>';
        
        tableContainer.innerHTML = html;
        tableBody = tableContainer.querySelector('tbody');
    }
    
    // 행 추가
    const fragment = document.createDocumentFragment();
    items.forEach((item, index) => {
        const rowId = item.item_code || item.id || index;
        const tr = document.createElement('tr');
        tr.className = 'clickable';
        tr.dataset.rowId = rowId;
        tr.onclick = () => goToDetail(rowId);
        
        let rowHtml = `<td class="col-center" onclick="event.stopPropagation()"><input type="checkbox" class="row-checkbox" value="${rowId}"></td>`;
        
        for (const key in schema) {
            const col = schema[key];
            const value = item[key];
            const align = col.align || (col.type === 'integer' ? 'right' : (col.type === 'boolean' ? 'center' : 'left'));
            rowHtml += `<td class="col-${align}">${formatValue(value, col.type, col.format)}</td>`;
        }
        tr.innerHTML = rowHtml;
        fragment.appendChild(tr);
    });
    
    tableBody.appendChild(fragment);
}

// 값 포맷팅
function formatValue(value, type, format) {
    if (value === null || value === undefined || value === '') {
        return '<span class="text-muted">-</span>';
    }
    
    switch(type) {
        case 'boolean':
            return value ? '<span class="badge badge-success">O</span>' : '<span class="badge badge-default">-</span>';
        case 'integer':
            return format === 'currency' ? value.toLocaleString('ko-KR') : value.toLocaleString('ko-KR');
        case 'datetime':
            return format === 'YYYY-MM-DD HH:mm' ? value.substring(0, 16).replace('T', ' ') : value;
        case 'date':
            return value.substring(0, 10).replace(/-/g, '. ');
        default:
            return value;
    }
}

// 검색 (Enter 키)
function handleSearch(event) {
    if (event.key === 'Enter') {
        loadData(true);
    }
}

// 전체 체크박스 토글
function toggleAllRows() {
    const checkAll = document.getElementById('checkAll');
    const checkboxes = document.querySelectorAll('.row-checkbox');
    checkboxes.forEach(cb => cb.checked = checkAll.checked);
}

// 선택된 행 가져오기
function getSelectedRows() {
    const checkboxes = document.querySelectorAll('.row-checkbox:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

// 상세 페이지로 이동
function goToDetail(itemCode) {
    const parts = itemCode.split('-');
    if (parts.length === 2) {
        window.location.href = `/service/parts/${parts[1]}/${parts[0]}`;
    } else {
        alert('상세 페이지로 이동: ' + itemCode);
    }
}

// 선택 삭제
function deleteSelected() {
    const selected = getSelectedRows();
    if (selected.length === 0) {
        alert('선택된 항목이 없습니다');
        return;
    }
    
    if (confirm(`${selected.length}개 항목을 삭제하시겠습니까?`)) {
        // TODO: API 호출
        console.log('삭제할 항목:', selected);
        alert('삭제 API 연동 예정');
    }
}

// 부품 등록 팝업 열기
async function openCreatePopup() {
    const modal = document.getElementById('createModal');
    const makerSelect = document.getElementById('regMaker');
    
    // Maker 목록 로드
    if (makerSelect.options.length <= 1) { // 기본 옵션만 있는 경우
        try {
            const response = await fetch('/api/v1/maker?limit=1000'); // 전체 목록 가져오기 위해 limit 증가
            if (response.ok) {
                const data = await response.json();
                const makers = data.items || [];
                
                // 이름순 정렬
                makers.sort((a, b) => a.name.localeCompare(b.name));
                
                makers.forEach(maker => {
                    // [수정] 이름이 비어있지 않은 경우에만 추가
                    if (maker.name && maker.name.trim()) {
                        const option = document.createElement('option');
                        option.value = maker.name; 
                        option.textContent = maker.name;
                        makerSelect.appendChild(option);
                    }
                });
            }
        } catch (e) {
            console.error('Maker load error:', e);
            alert('제조사 목록을 불러오지 못했습니다.');
        }
    }
    
    modal.style.display = 'flex';
}

// 대분류 직접 입력 토글
function toggleMajorManual() {
    const select = document.getElementById('regMajor');
    const manualInput = document.getElementById('regMajorManual');
    
    if (select.value === '기타') {
        manualInput.style.display = 'block';
        manualInput.focus();
    } else {
        manualInput.style.display = 'none';
        manualInput.value = '';
    }
}

// 팝업 닫기
function closeCreatePopup() {
    document.getElementById('createModal').style.display = 'none';
    
    // 입력 필드 초기화
    document.getElementById('regName').value = '';
    document.getElementById('regMinor').value = '';
    document.getElementById('regPrice').value = '0';
    document.getElementById('regEtc').value = '';
    document.getElementById('regMaker').value = '';
    
    // 대분류 초기화
    document.getElementById('regMajor').value = '전장 판넬 판금 및 명판';
    document.getElementById('regMajorManual').style.display = 'none';
    document.getElementById('regMajorManual').value = '';
    
    document.getElementById('regUL').checked = false;
    document.getElementById('regCE').checked = false;
    document.getElementById('regKC').checked = false;
}

// 부품 등록 제출
async function submitCreatePart() {
    const makerName = document.getElementById('regMaker').value;
    let major = document.getElementById('regMajor').value;
    const minor = document.getElementById('regMinor').value.trim();
    const name = document.getElementById('regName').value.trim();
    const unit = document.getElementById('regUnit').value.trim();
    const priceInput = document.getElementById('regPrice').value;
    const price = parseInt(priceInput) || 0;
    
    // 기타 선택 시 직접 입력값 사용
    if (major === '기타') {
        major = document.getElementById('regMajorManual').value.trim();
        if (!major) return alert('대분류를 입력해주세요.');
    }
    
    if (!makerName) return alert('Maker를 선택해주세요.');
    if (!major) return alert('Unit(대분류)를 선택해주세요.');
    if (!minor) return alert('품목(중분류)를 입력해주세요.');
    if (!name) return alert('모델명/규격을 입력해주세요.');
    if (!unit) return alert('단위를 입력해주세요.');
    
    const requestData = {
        maker_name: makerName,
        major_category: major,
        minor_category: minor,
        name: name,
        unit: unit,
        solo_price: price,
        ul: document.getElementById('regUL').checked,
        ce: document.getElementById('regCE').checked,
        kc: document.getElementById('regKC').checked,
        certification_etc: document.getElementById('regEtc').value.trim() || null
    };
    
    try {
        const response = await fetch('/api/v1/parts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        
        if (response.ok) {
            alert('부품이 등록되었습니다.');
            closeCreatePopup();
            loadData(true); // 목록 갱신 (초기화)
        } else {
            const error = await response.json();
            alert('등록 실패: ' + (error.detail || '알 수 없는 오류'));
        }
    } catch (e) {
        console.error('Submit error:', e);
        alert('등록 중 오류가 발생했습니다.');
    }
}
