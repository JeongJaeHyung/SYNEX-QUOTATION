let currentSkip = 0;
let currentLimit = 30; // 한 번에 30개씩
let totalItems = 0;
let isLoading = false;
let hasMore = true;
let observer;

// 페이지 로드 시
document.addEventListener('DOMContentLoaded', function() {
    initObserver();
    loadFilterOptions(); // 필터 옵션 로드
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

// 필터 옵션 로드 (제조사, 중분류)
async function loadFilterOptions() {
    try {
        // 제조사 필터 로드
        const makerResponse = await fetch('/api/v1/maker?limit=1000');
        if (makerResponse.ok) {
            const makerData = await makerResponse.json();
            const makers = makerData.items || [];
            const makerFilter = document.getElementById('makerFilter');

            makers.sort((a, b) => a.name.localeCompare(b.name));
            makers.forEach(maker => {
                if (maker.name && maker.name.trim()) {
                    const option = document.createElement('option');
                    option.value = maker.id;
                    option.textContent = maker.name;
                    makerFilter.appendChild(option);
                }
            });
        }

        // 중분류 필터 로드 (전체 부품에서 중복 제거)
        const partsResponse = await fetch('/api/v1/parts?limit=1000');
        if (partsResponse.ok) {
            const partsData = await partsResponse.json();
            const parts = partsData.items || [];
            const minorSet = new Set();

            parts.forEach(part => {
                if (part.minor_category && part.minor_category.trim()) {
                    minorSet.add(part.minor_category);
                }
            });

            const minorFilter = document.getElementById('minorFilter');
            const minorArray = Array.from(minorSet).sort();
            minorArray.forEach(minor => {
                const option = document.createElement('option');
                option.value = minor;
                option.textContent = minor;
                minorFilter.appendChild(option);
            });
        }
    } catch (error) {
        console.error('필터 옵션 로드 실패:', error);
    }
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
    const makerFilter = document.getElementById('makerFilter')?.value || '';
    const majorFilter = document.getElementById('majorFilter')?.value || '';
    const minorFilter = document.getElementById('minorFilter')?.value || '';

    let apiUrl = '/api/v1/parts?include_schema=true';
    apiUrl += `&skip=${currentSkip}&limit=${currentLimit}`;

    if (searchQuery) apiUrl += `&name=${encodeURIComponent(searchQuery)}`;
    if (makerFilter) apiUrl += `&maker_id=${encodeURIComponent(makerFilter)}`;
    if (majorFilter) apiUrl += `&major=${encodeURIComponent(majorFilter)}`;
    if (minorFilter) apiUrl += `&minor=${encodeURIComponent(minorFilter)}`;
    
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

// 상세/수정 모달 열기
async function goToDetail(itemCode) {
    const parts = itemCode.split('-');
    if (parts.length !== 2) {
        alert('잘못된 품목코드 형식입니다.');
        return;
    }

    const makerId = parts[0];
    const resourcesId = parts[1];

    try {
        // API로 부품 상세 정보 조회
        const response = await fetch(`/api/v1/parts/${resourcesId}/${makerId}`);
        if (!response.ok) {
            throw new Error('부품 정보를 불러올 수 없습니다.');
        }

        const partData = await response.json();
        openEditPopup(partData);
    } catch (error) {
        console.error('Error:', error);
        alert(error.message);
    }
}

// 수정 모달 열기
function openEditPopup(partData) {
    const modal = document.getElementById('editModal');

    // hidden 필드에 ID 저장
    document.getElementById('editPartsId').value = partData.id;
    document.getElementById('editMakerId').value = partData.maker_id;

    // 폼 필드에 데이터 채우기
    document.getElementById('editMakerName').value = partData.maker_name;

    // 대분류: 기존 옵션에 있으면 선택, 없으면 '기타' 선택 후 수동 입력
    const majorSelect = document.getElementById('editMajor');
    const majorManualInput = document.getElementById('editMajorManual');
    const majorOptions = Array.from(majorSelect.options).map(opt => opt.value);

    if (majorOptions.includes(partData.major_category)) {
        majorSelect.value = partData.major_category;
        majorManualInput.style.display = 'none';
        majorManualInput.value = '';
    } else {
        majorSelect.value = '기타';
        majorManualInput.style.display = 'block';
        majorManualInput.value = partData.major_category;
    }

    document.getElementById('editMinor').value = partData.minor_category;
    document.getElementById('editName').value = partData.name;
    document.getElementById('editUnit').value = partData.unit;
    document.getElementById('editPrice').value = partData.solo_price;

    // 인증 체크박스
    document.getElementById('editUL').checked = partData.ul || false;
    document.getElementById('editCE').checked = partData.ce || false;
    document.getElementById('editKC').checked = partData.kc || false;
    document.getElementById('editEtc').value = partData.etc || '';

    modal.style.display = 'flex';
}

// 수정 모달 닫기
function closeEditPopup() {
    document.getElementById('editModal').style.display = 'none';
}

// 대분류 수동 입력 토글 (수정 모달용)
function toggleEditMajorManual() {
    const select = document.getElementById('editMajor');
    const manualInput = document.getElementById('editMajorManual');

    if (select.value === '기타') {
        manualInput.style.display = 'block';
        manualInput.focus();
    } else {
        manualInput.style.display = 'none';
        manualInput.value = '';
    }
}

// 부품 수정 제출
async function submitEditPart() {
    const partsId = document.getElementById('editPartsId').value;
    const makerId = document.getElementById('editMakerId').value;

    let major = document.getElementById('editMajor').value;
    const minor = document.getElementById('editMinor').value.trim();
    const name = document.getElementById('editName').value.trim();
    const unit = document.getElementById('editUnit').value.trim();
    const priceInput = document.getElementById('editPrice').value;
    const price = parseInt(priceInput) || 0;

    // 기타 선택 시 직접 입력값 사용
    if (major === '기타') {
        major = document.getElementById('editMajorManual').value.trim();
        if (!major) return alert('대분류를 입력해주세요.');
    }

    if (!major) return alert('Unit(대분류)를 선택해주세요.');
    if (!minor) return alert('품목(중분류)를 입력해주세요.');
    if (!name) return alert('모델명/규격을 입력해주세요.');
    if (!unit) return alert('단위를 입력해주세요.');

    const requestData = {
        major_category: major,
        minor_category: minor,
        name: name,
        unit: unit,
        solo_price: price,
        ul: document.getElementById('editUL').checked,
        ce: document.getElementById('editCE').checked,
        kc: document.getElementById('editKC').checked,
        certification_etc: document.getElementById('editEtc').value.trim() || null
    };

    try {
        const response = await fetch(`/api/v1/parts/${partsId}/${makerId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });

        if (response.ok) {
            alert('부품이 수정되었습니다.');
            closeEditPopup();
            loadData(true); // 목록 갱신
        } else {
            const error = await response.json();
            alert('수정 실패: ' + (error.detail || '알 수 없는 오류'));
        }
    } catch (e) {
        console.error('Submit error:', e);
        alert('수정 중 오류가 발생했습니다.');
    }
}

// 선택 삭제
async function deleteSelected() {
    const selected = getSelectedRows();
    if (selected.length === 0) {
        alert('선택된 항목이 없습니다');
        return;
    }

    if (!confirm(`${selected.length}개 항목을 삭제하시겠습니까?\n삭제된 데이터는 복구할 수 없습니다.`)) {
        return;
    }

    let successCount = 0;
    let failCount = 0;
    const failedItems = [];

    for (const itemCode of selected) {
        try {
            // item_code 형식: "maker_id-resources_id" (예: "T000-000001")
            const parts = itemCode.split('-');
            if (parts.length !== 2) {
                console.error('Invalid item_code format:', itemCode);
                failCount++;
                failedItems.push(itemCode);
                continue;
            }

            const makerId = parts[0];
            const resourcesId = parts[1];

            // API 경로: /api/v1/parts/{parts_id}/{maker_id}
            const response = await fetch(`/api/v1/parts/${resourcesId}/${makerId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                successCount++;
            } else {
                failCount++;
                failedItems.push(itemCode);
                const error = await response.json();
                console.error(`Delete failed for ${itemCode}:`, error);
            }
        } catch (e) {
            failCount++;
            failedItems.push(itemCode);
            console.error(`Delete error for ${itemCode}:`, e);
        }
    }

    // 결과 메시지
    let message = '';
    if (successCount > 0) {
        message += `${successCount}개 항목이 삭제되었습니다.`;
    }
    if (failCount > 0) {
        message += `\n${failCount}개 항목 삭제에 실패했습니다.`;
    }
    alert(message);

    // 목록 새로고침
    loadData(true);
}

// 부품 등록 팝업 열기
async function openCreatePopup() {
    const modal = document.getElementById('createModal');
    const makerDatalist = document.getElementById('makerList');

    // Maker 목록 로드 (datalist가 비어있는 경우)
    if (makerDatalist.options.length === 0) {
        try {
            const response = await fetch('/api/v1/maker?limit=1000'); // 전체 목록 가져오기 위해 limit 증가
            if (response.ok) {
                const data = await response.json();
                const makers = data.items || [];

                // 이름순 정렬
                makers.sort((a, b) => a.name.localeCompare(b.name));

                makers.forEach(maker => {
                    // 이름이 비어있지 않은 경우에만 추가
                    if (maker.name && maker.name.trim()) {
                        const option = document.createElement('option');
                        option.value = maker.name;
                        makerDatalist.appendChild(option);
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
    let makerName = document.getElementById('regMaker').value.trim();
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

    if (!makerName) return alert('Maker를 선택하거나 입력해주세요.');
    if (!major) return alert('Unit(대분류)를 선택해주세요.');
    if (!minor) return alert('품목(중분류)를 입력해주세요.');
    if (!name) return alert('모델명/규격을 입력해주세요.');
    if (!unit) return alert('단위를 입력해주세요.');

    // 제조사 존재 여부 확인 및 필요시 생성
    const makerExists = await checkAndCreateMaker(makerName);
    if (!makerExists) return; // 사용자가 제조사 등록을 취소한 경우

    // 대분류 기타 선택 시 확인
    const majorConfirmed = await checkMajorCategory(major);
    if (!majorConfirmed) return; // 사용자가 대분류 등록을 취소한 경우

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

// 제조사 존재 여부 확인 및 필요시 생성
async function checkAndCreateMaker(makerName) {
    try {
        // 제조사 목록에서 해당 이름 검색
        const searchRes = await fetch(`/api/v1/maker/search?query=${encodeURIComponent(makerName)}`);
        if (searchRes.ok) {
            const searchData = await searchRes.json();
            const existingMaker = searchData.items?.find(m => m.name === makerName);

            if (existingMaker) {
                return true; // 이미 존재하는 제조사
            }
        }

        // 제조사가 없으면 사용자에게 확인
        const shouldCreate = confirm(`"${makerName}"은(는) 등록되지 않은 제조사입니다.\n등록하시겠습니까?`);
        if (!shouldCreate) {
            return false; // 사용자가 취소
        }

        // 제조사 생성
        const createRes = await fetch('/api/v1/maker', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: makerName })
        });

        if (createRes.ok) {
            alert(`제조사 "${makerName}"이(가) 등록되었습니다.`);
            return true;
        } else {
            const error = await createRes.json();
            alert('제조사 등록 실패: ' + (error.detail || '알 수 없는 오류'));
            return false;
        }
    } catch (e) {
        console.error('Maker check/create error:', e);
        alert('제조사 확인 중 오류가 발생했습니다.');
        return false;
    }
}

// 대분류 확인 (기타로 입력한 경우)
async function checkMajorCategory(majorCategory) {
    // 기본 대분류 목록
    const standardMajorCategories = [
        '전장 판넬 판금 및 명판',
        '판넬 차단기류',
        'PLC Set',
        'Touch Screen',
        '판넬 주요자재',
        '판넬 기타자재',
        '케이블 및 기타 잡자재'
    ];

    // 기본 대분류인지 확인
    if (standardMajorCategories.includes(majorCategory)) {
        return true; // 표준 대분류는 확인 불필요
    }

    // 새로운 대분류인 경우 사용자에게 확인
    const shouldCreate = confirm(`"${majorCategory}"은(는) 등록되지 않은 대분류입니다.\n등록하시겠습니까?`);
    return shouldCreate;
}
