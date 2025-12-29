// default_list.js

/**
 * 전역 상태 관리
 */
let currentSkip = 0;
let currentLimit = 20;
let totalItems = 0;

/**
 * 초기 로드
 */
document.addEventListener('DOMContentLoaded', function() {
    loadData();
});

/**
 * 서버로부터 데이터 가져오기
 */
async function loadData() {
    const loading = document.getElementById('loading');
    const tableContainer = document.getElementById('tableContainer');
    const pagination = document.getElementById('pagination');

    // UI 초기화
    loading.style.display = 'block';
    tableContainer.innerHTML = '';
    pagination.style.display = 'none';

    const apiUrl = `/api/v1/quotation/general?include_schema=true&skip=${currentSkip}&limit=${currentLimit}`;

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) throw new Error('API 호출 실패');

        const data = await response.json();
        totalItems = data.total || 0;

        renderTable(data.schema, data.items);
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

/**
 * 테이블 생성 및 DOM 삽입
 */
function renderTable(schema, items) {
    const tableContainer = document.getElementById('tableContainer');

    if (!items || items.length === 0) {
        tableContainer.innerHTML = '<div class="empty-state">데이터가 없습니다</div>';
        return;
    }

    let totalRatio = Object.values(schema).reduce((acc, col) => acc + (col.ratio || 1), 0);

    let html = '<div class="table-container"><table class="data-table" id="quotationTable">';

    // Header
    html += '<thead><tr>';
    html += '<th class="col-center" style="width: 50px"><input type="checkbox" id="selectAll" onchange="toggleSelectAll(this)"></th>';
    for (const key in schema) {
        const col = schema[key];
        const width = ((col.ratio || 1) / totalRatio * 100).toFixed(1);
        html += `<th class="col-left" style="width: ${width}%">${col.title}</th>`;
    }
    html += '</tr></thead><tbody>';

    // Rows
    items.forEach((item) => {
        html += `<tr>`;
        html += `<td class="col-center"><input type="checkbox" class="row-checkbox" value="${item.id}"></td>`;
        for (const key in schema) {
            const col = schema[key];
            html += `<td class="col-left clickable" onclick="goToDetail('${item.id}')">${formatValue(item[key], col.type, col.format)}</td>`;
        }
        html += '</tr>';
    });

    html += '</tbody></table></div>';
    tableContainer.innerHTML = html;
}

/**
 * 값 포맷팅 (날짜, NULL 처리 등)
 */
function formatValue(value, type, format) {
    if (value === null || value === undefined || value === '') {
        return '<span class="text-muted">-</span>';
    }

    switch(type) {
        case 'datetime':
            return format === 'YYYY-MM-DD HH:mm' ? value.substring(0, 16).replace('T', ' ') : value;
        case 'date':
            return value.substring(0, 10).replace(/-/g, '. ');
        default:
            return value;
    }
}

/**
 * 페이지네이션 버튼 상태 및 정보 업데이트
 */
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

        prevBtn.disabled = (currentSkip === 0);
        nextBtn.disabled = (currentSkip + currentLimit >= totalItems);
    } else {
        pagination.style.display = 'none';
    }
}

/**
 * 이전 페이지 이동
 */
function goToPrevPage() {
    if (currentSkip >= currentLimit) {
        currentSkip -= currentLimit;
        loadData();
    }
}

/**
 * 다음 페이지 이동
 */
function goToNextPage() {
    if (currentSkip + currentLimit < totalItems) {
        currentSkip += currentLimit;
        loadData();
    }
}

/**
 * 페이지 이동 함수들
 */
function createQuotation() {
    window.location.href = '/service/quotation/general/form?mode=create';
}

function goToDetail(quotationId) {
    window.location.href = `/service/quotation/general/form?mode=view&id=${quotationId}`;
}

/**
 * 전체 선택/해제
 */
function toggleSelectAll(checkbox) {
    const checkboxes = document.querySelectorAll('.row-checkbox');
    checkboxes.forEach(cb => cb.checked = checkbox.checked);
}

/**
 * 선택된 행 가져오기
 */
function getSelectedRows() {
    const checkboxes = document.querySelectorAll('.row-checkbox:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

/**
 * 선택 삭제
 */
async function deleteSelected() {
    const selected = getSelectedRows();
    if (selected.length === 0) {
        alert('선택된 항목이 없습니다');
        return;
    }

    if (!confirm(`선택한 ${selected.length}개의 견적서를 삭제하시겠습니까?\n\n삭제 시 관련된 모든 폴더, 갑지, 을지, 내정가비교서가 함께 삭제됩니다.`)) {
        return;
    }

    let successCount = 0;
    let failCount = 0;

    for (const generalId of selected) {
        try {
            const response = await fetch(`/api/v1/quotation/general/${generalId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                successCount++;
            } else {
                failCount++;
            }
        } catch (error) {
            failCount++;
            console.error(`Delete error for ${generalId}:`, error);
        }
    }

    let message = '';
    if (successCount > 0) {
        message += `${successCount}개 항목이 삭제되었습니다.`;
    }
    if (failCount > 0) {
        message += `\n${failCount}개 항목 삭제에 실패했습니다.`;
    }
    alert(message);

    loadData(); // 목록 새로고침
}
