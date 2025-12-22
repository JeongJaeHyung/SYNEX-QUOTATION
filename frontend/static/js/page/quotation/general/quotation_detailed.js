/**
 * 견적서(을지) 상세 - View/Edit 모드 및 실시간 편집 로직
 * API: /api/v1/quotation/detailed/{id}
 */

let detailedId = null;
let originalData = null;
let pageMode = 'view'; // 초기 모드: 'view' (조회)

// ============================================================================
// 페이지 초기화
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // 1. URL에서 ID 추출
    const pathParts = window.location.pathname.split('/');
    detailedId = pathParts[pathParts.length - 1];
    
    if (detailedId) {
        loadDetailedData(detailedId);
    }

    // 2. 실시간 계산 이벤트 위임 (수정 모드일 때만 작동)
    const tbody = document.querySelector('#detailedTable tbody');
    if (tbody) {
        tbody.addEventListener('input', function(e) {
            if (pageMode !== 'edit') return;

            const row = e.target.closest('.data-row');
            if (!row) return;

            // 수량이나 단가가 변경될 때만 계산 실행
            if (e.target.classList.contains('edit-qty') || e.target.classList.contains('edit-price')) {
                updateRowSubtotal(row);
                calculateGrandTotal();
            }
        });
    }
});

// ============================================================================
// 데이터 로드 및 모드 관리
// ============================================================================

async function loadDetailedData(id) {
    try {
        const response = await fetch(`/api/v1/quotation/detailed/${id}`);
        if (!response.ok) throw new Error('데이터 로드 실패');
        
        originalData = await response.json();
        
        // 테이블 렌더링 후 초기 모드 설정
        renderDetailedTable(originalData.detailed_resources);
        toggleEditMode('view');
        
        document.getElementById('loading').style.display = 'none';
        document.getElementById('detailedTable').style.display = 'table';
    } catch (error) {
        console.error(error);
        alert('데이터를 불러오는데 실패했습니다.');
    }
}

/**
 * View/Edit 모드 전환 함수
 * @param {string} mode - 'view' 또는 'edit'
 */
function toggleEditMode(mode) {
    pageMode = mode;
    const table = document.getElementById('detailedTable');
    const title = document.getElementById('pageTitle');
    const viewActions = document.getElementById('viewActions');
    const editActions = document.getElementById('editActions');

    // 1. 테이블 데이터 속성 변경 (CSS 바인딩용)
    table.dataset.mode = mode;
    
    // 2. 모든 편집 가능 셀의 속성 일괄 변경
    const editableCells = table.querySelectorAll('[contenteditable]');
    editableCells.forEach(cell => {
        cell.contentEditable = (mode === 'edit');
    });

    // 3. 플로팅 사이드바 버튼 그룹 및 제목 토글
    if (mode === 'edit') {
        title.textContent = '상세 견적서 (수정 중)';
        viewActions.style.display = 'none';
        editActions.style.display = 'flex';
    } else {
        title.textContent = '상세 견적서 (을지)';
        viewActions.style.display = 'flex';
        editActions.style.display = 'none';
        
        // 취소 시 혹은 초기화 시 원본 데이터로 복구가 필요하면 다시 렌더링
        if (originalData) renderDetailedTable(originalData.detailed_resources);
    }
}

// ============================================================================
// 테이블 렌더링 및 계산 로직
// ============================================================================

function renderDetailedTable(resources) {
    const tbody = document.querySelector('#detailedTable tbody');
    tbody.innerHTML = '';
    
    const groups = groupByMachineThenMajor(resources);
    let html = '';
    let rowNo = 1;

    Object.keys(groups).forEach(machine => {
        Object.keys(groups[machine]).forEach(major => {
            const items = groups[machine][major];
            html += `<tr class="section-title"><td colspan="7">● ${machine} - ${major} 상세 내역</td></tr>`;
            
            items.forEach(item => {
                html += `
                <tr class="data-row" 
                    data-machine="${item.machine_name}" 
                    data-major="${item.major}" 
                    data-minor="${item.minor}">
                    <td class="text-center">${rowNo++}</td>
                    <td>${item.minor}</td>
                    <td contenteditable="false" class="edit-unit text-center">${item.unit || '식'}</td>
                    <td contenteditable="false" class="edit-qty text-right">${item.compare}</td>
                    <td contenteditable="false" class="edit-price text-right">${formatNumber(item.solo_price)}</td>
                    <td class="row-subtotal text-right">${formatNumber(item.subtotal)}</td>
                    <td contenteditable="false" class="edit-desc">${item.description || ''}</td>
                </tr>`;
            });
        });
    });
    
    tbody.innerHTML = html;
    calculateGrandTotal();
}

function updateRowSubtotal(row) {
    const qty = parseNumber(row.querySelector('.edit-qty').textContent);
    const price = parseNumber(row.querySelector('.edit-price').textContent);
    const subtotal = qty * price;
    row.querySelector('.row-subtotal').textContent = formatNumber(subtotal);
}

function calculateGrandTotal() {
    const subtotals = document.querySelectorAll('.row-subtotal');
    let total = 0;
    subtotals.forEach(cell => total += parseNumber(cell.textContent));
    
    const tfoot = document.querySelector('#detailedTable tfoot');
    if (tfoot) {
        tfoot.innerHTML = `
            <tr class="total-row">
                <td colspan="5" class="text-center">합 계 (VAT 별도)</td>
                <td class="total-amount-cell">${formatNumber(total)}</td>
                <td></td>
            </tr>`;
    }
}

// ============================================================================
// 서버 데이터 저장 (PUT)
// ============================================================================

async function saveDetailedData() {
    const saveBtn = document.getElementById('saveBtn');
    const rows = document.querySelectorAll('.data-row');
    const resources = [];

    // 화면의 수정된 데이터를 객체 배열로 수집
    rows.forEach(row => {
        resources.push({
            machine_name: row.dataset.machine,
            major: row.dataset.major,
            minor: row.dataset.minor,
            unit: row.querySelector('.edit-unit').textContent.trim(),
            compare: parseNumber(row.querySelector('.edit-qty').textContent),
            solo_price: parseNumber(row.querySelector('.edit-price').textContent),
            description: row.querySelector('.edit-desc').textContent.trim()
        });
    });

    const payload = {
        creator: originalData.creator,
        description: originalData.description,
        detailed_resources: resources
    };

    if (!confirm('변경사항을 저장하시겠습니까?')) return;

    saveBtn.disabled = true;
    const originalText = saveBtn.textContent;
    saveBtn.textContent = '저장 중...';

    try {
        const response = await fetch(`/api/v1/quotation/detailed/${detailedId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const result = await response.json();
            originalData = result; // 최신 데이터로 로컬 캐시 갱신
            alert('성공적으로 저장되었습니다.');
            toggleEditMode('view'); // 저장 후 조회 모드로 복귀
        } else {
            const err = await response.json();
            throw new Error(err.detail || '저장 실패');
        }
    } catch (e) {
        console.error(e);
        alert('저장 중 오류가 발생했습니다: ' + e.message);
    } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = originalText;
    }
}

// ============================================================================
// 유틸리티 함수
// ============================================================================

function formatNumber(n) { 
    return (n || 0).toLocaleString('ko-KR'); 
}

function parseNumber(s) { 
    if (!s) return 0;
    return parseInt(s.toString().replace(/,/g, '')) || 0; 
}

function groupByMachineThenMajor(res) {
    return res.reduce((acc, curr) => {
        if (!acc[curr.machine_name]) acc[curr.machine_name] = {};
        if (!acc[curr.machine_name][curr.major]) acc[curr.machine_name][curr.major] = [];
        acc[curr.machine_name][curr.major].push(curr);
        return acc;
    }, {});
}

function goBack() { 
    window.history.back(); 
}