let currentSkip = 0;
let currentLimit = 20;
let totalItems = 0;

// 페이지 로드 시 데이터 가져오기
document.addEventListener('DOMContentLoaded', function() {
    loadData();
});

// 데이터 로드
async function loadData() {
    const loading = document.getElementById('loading');
    const tableContainer = document.getElementById('tableContainer');
    const pagination = document.getElementById('pagination');
    
    // 로딩 표시
    loading.style.display = 'block';
    tableContainer.innerHTML = '';
    pagination.style.display = 'none';
    
    // 검색 조건
    const searchQuery = document.getElementById('searchInput').value;
    
    // API URL 구성
    let apiUrl = '/api/v1/quotation/machine?include_schema=true';
    apiUrl += `&skip=${currentSkip}&limit=${currentLimit}`;
    
    if (searchQuery) {
        // 검색 API 사용
        apiUrl = `/api/v1/quotation/machine/search?search=${encodeURIComponent(searchQuery)}`;
        apiUrl += `&include_schema=true&skip=${currentSkip}&limit=${currentLimit}`;
    }
    
    try {
        const response = await fetch(apiUrl);
        
        if (!response.ok) {
            throw new Error('API 호출 실패');
        }
        
        const data = await response.json();
        
        // 데이터 저장
        totalItems = data.total || 0;
        
        // 테이블 렌더링
        renderTable(data.schema, data.items);
        
        // 페이지네이션 업데이트
        updatePagination();
        
    } catch (error) {
        console.error('Error:', error);
        tableContainer.innerHTML = `
            <div class="empty-state" style="color: #ef4444;">
                데이터를 불러오는데 실패했습니다.<br>
                <small>${error.message}</small>
            </div>
        `;
    } finally {
        loading.style.display = 'none';
    }
}

// 테이블 렌더링
function renderTable(schema, items) {
    const tableContainer = document.getElementById('tableContainer');
    
    if (!items || items.length === 0) {
        tableContainer.innerHTML = '<div class="empty-state">데이터가 없습니다</div>';
        return;
    }
    
    // ratio 합계 계산
    let totalRatio = 0;
    for (const key in schema) {
        totalRatio += schema[key].ratio || 1;
    }
    
    // 테이블 HTML 생성
    let html = '<div class="table-container"><table class="data-table" id="machineTable">';

    // 헤더
    html += '<thead><tr>';
    html += '<th style="width: 40px"><input type="checkbox" id="selectAll" onchange="toggleSelectAll(this)"></th>';

    for (const key in schema) {
        const col = schema[key];
        const width = ((col.ratio || 1) / totalRatio * 100).toFixed(1);
        const align = col.align || 'left';
        html += `<th class="col-${align}" style="width: ${width}%">${col.title}</th>`;
    }

    html += '</tr></thead><tbody>';
    
    // 데이터 행
    items.forEach((item) => {
        const machineId = item.id;
        html += `<tr class="clickable" data-machine-id="${machineId}">`;
        html += `<td onclick="event.stopPropagation()"><input type="checkbox" class="row-checkbox" value="${machineId}"></td>`;

        for (const key in schema) {
            const col = schema[key];
            const value = item[key];
            const align = col.align || 'left';

            html += `<td class="col-${align}" onclick="goToDetail('${machineId}')">`;
            html += formatValue(value, col.type, col.format);
            html += '</td>';
        }

        html += '</tr>';
    });
    
    html += '</tbody></table></div>';
    
    tableContainer.innerHTML = html;
}

// 값 포맷팅
function formatValue(value, type, format) {
    if (value === null || value === undefined || value === '') {
        return '<span class="text-muted">-</span>';
    }
    
    switch(type) {
        case 'boolean':
            return value ? 
                '<span class="badge badge-success">O</span>' : 
                '<span class="badge badge-default">X</span>';
        
        case 'integer':
            if (format === 'currency') {
                return value.toLocaleString('ko-KR');
            }
            return value.toLocaleString('ko-KR');
        
        case 'datetime':
            if (format === 'YYYY-MM-DD HH:mm') {
                return value.substring(0, 16).replace('T', ' ');
            }
            return value;
        
        case 'date':
            return value.substring(0, 10).replace(/-/g, '. ');
        
        default:
            return value;
    }
}

// 페이지네이션 업데이트
function updatePagination() {
    const pagination = document.getElementById('pagination');
    const pageInfo = document.getElementById('pageInfo');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    if (totalItems > currentLimit) {
        pagination.style.display = 'flex';
        
        const start = currentSkip + 1;
        const end = Math.min(currentSkip + currentLimit, totalItems);
        pageInfo.textContent = `전체 ${totalItems}개 중 ${start} - ${end}`;
        
        prevBtn.disabled = currentSkip === 0;
        nextBtn.disabled = currentSkip + currentLimit >= totalItems;
    } else {
        pagination.style.display = 'none';
    }
}

// 이전 페이지
function goToPrevPage() {
    if (currentSkip >= currentLimit) {
        currentSkip -= currentLimit;
        loadData();
    }
}

// 다음 페이지
function goToNextPage() {
    if (currentSkip + currentLimit < totalItems) {
        currentSkip += currentLimit;
        loadData();
    }
}

// 검색 (Enter 키)
function handleSearch(event) {
    if (event.key === 'Enter') {
        currentSkip = 0; // 검색 시 첫 페이지로
        loadData();
    }
}

// 견적서 생성 페이지로 이동
function createMachine() {
    window.location.href = '/service/quotation/machine/form?mode=create';
}

// 상세 페이지로 이동 (View 모드)
function goToDetail(machineId) {
    window.location.href = `/service/quotation/machine/form?mode=view&id=${machineId}`;
}

// 전체 선택/해제
function toggleSelectAll(checkbox) {
    const checkboxes = document.querySelectorAll('.row-checkbox');
    checkboxes.forEach(cb => cb.checked = checkbox.checked);
}

// 선택된 항목 가져오기
function getSelectedRows() {
    const checkboxes = document.querySelectorAll('.row-checkbox:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

// 선택 삭제
async function deleteSelected() {
    const selected = getSelectedRows();
    if (selected.length === 0) {
        alert('선택된 항목이 없습니다');
        return;
    }

    if (!confirm(`${selected.length}개 견적서를 삭제하시겠습니까?\n삭제된 데이터는 복구할 수 없습니다.`)) {
        return;
    }

    let successCount = 0;
    let failCount = 0;
    const failedItems = [];

    for (const machineId of selected) {
        try {
            const response = await fetch(`/api/v1/quotation/machine/${machineId}`, {
                method: 'DELETE'
            });

            if (response.ok || response.status === 204) {
                successCount++;
            } else {
                failCount++;
                failedItems.push(machineId);
                const error = await response.json().catch(() => ({}));
                console.error(`Delete failed for ${machineId}:`, error);
            }
        } catch (e) {
            failCount++;
            failedItems.push(machineId);
            console.error(`Delete error for ${machineId}:`, e);
        }
    }

    // 결과 메시지
    let message = '';
    if (successCount > 0) {
        message += `${successCount}개 견적서가 삭제되었습니다.`;
    }
    if (failCount > 0) {
        message += `\n${failCount}개 견적서 삭제에 실패했습니다.`;
    }
    alert(message);

    // 목록 새로고침
    loadData();
}
