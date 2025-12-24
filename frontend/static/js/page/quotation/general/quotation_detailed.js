/**
 * 견적서(을지) 상세 - 8개 컬럼 & 장비명 셀 병합 로직 통합
 */

let detailedId = null;
let originalData = null;
let pageMode = 'view'; 

document.addEventListener('DOMContentLoaded', function() {
    const pathParts = window.location.pathname.split('/');
    detailedId = pathParts[pathParts.length - 1];
    
    if (detailedId) {
        loadDetailedData(detailedId);
    }

    const tbody = document.querySelector('#detailedTable tbody');
    if (tbody) {
        tbody.addEventListener('input', function(e) {
            if (pageMode !== 'edit') return;
            const row = e.target.closest('.data-row');
            if (row && (e.target.classList.contains('edit-qty') || e.target.classList.contains('edit-price'))) {
                updateRowSubtotal(row);
                calculateGrandTotal();
            }
        });
    }
});

async function loadDetailedData(id) {
    try {
        const response = await fetch(`/api/v1/quotation/detailed/${id}`);
        if (!response.ok) throw new Error('데이터 로드 실패');
        originalData = await response.json();
        
        renderDetailedTable(originalData.detailed_resources);
        document.getElementById('quotationDescription').innerText = originalData.description || '';
        toggleEditMode('view');
        
        document.getElementById('loading').style.display = 'none';
        document.getElementById('detailedTable').style.display = 'table';
    } catch (error) {
        console.error(error);
        alert('데이터를 불러오는데 실패했습니다.');
    }
}

function toggleEditMode(mode) {
    pageMode = mode;
    const table = document.getElementById('detailedTable');
    const title = document.getElementById('pageTitle');
    const viewActions = document.getElementById('viewActions');
    const editActions = document.getElementById('editActions');
    const descriptionBox = document.getElementById('quotationDescription'); // 비고란 선택

    table.dataset.mode = mode;
    
    // 테이블 내 셀 편집 제어
    const editableCells = table.querySelectorAll('[contenteditable]');
    editableCells.forEach(cell => {
        cell.contentEditable = (mode === 'edit');
    });

    // [추가] 하단 비고란 편집 제어
    descriptionBox.contentEditable = (mode === 'edit');

    if (mode === 'edit') {
        viewActions.style.display = 'none';
        editActions.style.display = 'flex';
    } else {
        title.textContent = '상세 견적서 (을지)';
        viewActions.style.display = 'flex';
        editActions.style.display = 'none';
        if (originalData) {
            renderDetailedTable(originalData.detailed_resources);
            // [추가] 취소 시 비고란 데이터 원복
            descriptionBox.innerText = originalData.description || '';
        }
    }
}

function renderDetailedTable(resources) {
    const tbody = document.querySelector('#detailedTable tbody');
    tbody.innerHTML = '';
    
    const majorOrder = ['자재비', '인건비', '출장 경비', '관리비'];
    const groups = groupByMajorThenMachine(resources);
    
    let html = '';
    let rowNo = 1;

    const renderSection = (major) => {
        const machines = groups[major];
        let majorTotal = 0; // 해당 대분류의 합계를 저장할 변수
        
        // 1. 대분류 섹션 타이틀 행
        html += `<tr class="section-title-row"><td colspan="8">${major} 상세 내역</td></tr>`;
        
        Object.keys(machines).forEach(machineName => {
            const items = machines[machineName];
            const rowCount = items.length;

            items.forEach((item, idx) => {
                const subtotal = item.subtotal || 0;
                majorTotal += subtotal; // 합계 누적

                html += `
                <tr class="data-row" 
                    data-machine="${item.machine_name}" 
                    data-major="${item.major}" 
                    data-minor="${item.minor}">
                    <td class="text-center">${rowNo++}</td>`;
                
                if (idx === 0) {
                    html += `<td rowspan="${rowCount}" class="machine-name-cell text-center">${machineName}</td>`;
                }

                html += `
                    <td>${item.minor}</td>
                    <td contenteditable="false" class="edit-qty text-right">${item.compare}</td>
                    <td contenteditable="false" class="edit-unit text-center">${item.unit || '식'}</td>
                    <td contenteditable="false" class="edit-price text-right">${formatNumber(item.solo_price)}</td>
                    <td class="row-subtotal text-right">${formatNumber(subtotal)}</td>
                    <td contenteditable="false" class="edit-desc">${item.description || ''}</td>
                </tr>`;
            });
        });

        // 2. 대분류별 총 합계 행 추가
        html += `
        <tr class="major-subtotal-row">
            <td colspan="6" class="text-center">${major} 총 합계</td>
            <td class="text-right font-bold">${formatNumber(majorTotal)}</td>
            <td></td>
        </tr>`;
    };

    majorOrder.forEach(major => { if (groups[major]) renderSection(major); });
    Object.keys(groups).forEach(major => { if (!majorOrder.includes(major)) renderSection(major); });
    
    tbody.innerHTML = html;
    calculateGrandTotal(); // 전체 총계 계산
}

function groupByMajorThenMachine(res) {
    return res.reduce((acc, curr) => {
        const major = curr.major || '기타';
        const machine = curr.machine_name || '미분류';
        if (!acc[major]) acc[major] = {};
        if (!acc[major][machine]) acc[major][machine] = [];
        acc[major][machine].push(curr);
        return acc;
    }, {});
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
                <td colspan="6" class="text-center">합 계 (VAT 별도)</td>
                <td class="total-amount-cell">${formatNumber(total)}</td>
                <td></td>
            </tr>`;
    }
}

async function saveDetailedData() {
    const saveBtn = document.getElementById('saveBtn');
    const rows = document.querySelectorAll('.data-row');
    const descriptionBox = document.getElementById('quotationDescription');
    const resources = [];

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
        description: descriptionBox.innerText.trim(), // [수정] 수집된 비고란 텍스트 적용
        detailed_resources: resources
    };

    if (!confirm('변경사항을 저장하시겠습니까?')) return;
    saveBtn.disabled = true;
    try {
        const response = await fetch(`/api/v1/quotation/detailed/${detailedId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (response.ok) {
            originalData = await response.json();
            alert('성공적으로 저장되었습니다.');
            toggleEditMode('view');
        }
    } finally {
        saveBtn.disabled = false;
    }
}

function formatNumber(n) { return (n || 0).toLocaleString('ko-KR'); }
function parseNumber(s) {
    if (!s || s.trim() === '-' || s.trim() === '') return 0;
    return parseInt(s.toString().replace(/,/g, '')) || 0;
}
function goBack() { window.history.back(); }

// PDF 내보내기
function exportToPDF() {
    const projectName = originalData?.title || '상세견적서';
    const docType = '을지';
    const timestamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14);
    const filename = `${projectName}_${timestamp}.pdf`;

    fetch('/api/save-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            url: window.location.href,
            filename: filename,
            projectName: projectName,
            docType: docType
        })
    })
    .then(res => res.json())
    .then(result => {
        if (result.success) {
            alert('PDF가 저장되었습니다:\n' + result.path);
        } else if (result.message !== '저장이 취소되었습니다.') {
            alert('저장 실패: ' + result.message);
        }
    })
    .catch(err => {
        console.error('저장 오류:', err);
        alert('PDF 저장 중 오류가 발생했습니다.');
    });
}