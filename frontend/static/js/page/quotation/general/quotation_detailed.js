/**
 * 견적서(을지) 상세 - 8개 컬럼 & 장비명 셀 병합 & 엑셀 추출 통합
 * 버그 수정: '출장경비' 공백 불일치 해결 및 카테고리 누락 방지 로직 적용
 */

let detailedId = null;
let originalData = null; // 모든 데이터의 기준
let pageMode = 'view'; 

// [고도화] 출력용 타이틀 매핑: 데이터의 공백 유무에 상관없이 일관된 타이틀 출력
const MAJOR_DISPLAY_MAP = {
    '자재비': '자재비 상세 내역',
    '인건비': '인건비 상세 내역',
    '출장경비': '경비 상세 내역_국내',
    '관리비': '관리비 상세 내역'
};

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
        
        const loading = document.getElementById('loading');
        if (loading) loading.style.display = 'none';
        document.getElementById('detailedTable').style.display = 'table';
        toggleEditMode('view');
    } catch (error) {
        console.error(error);
        alert('데이터를 불러오는데 실패했습니다.');
    }
}

function toggleEditMode(mode) {
    pageMode = mode;
    const table = document.getElementById('detailedTable');
    const viewActions = document.getElementById('viewActions');
    const editActions = document.getElementById('editActions');
    const descriptionBox = document.getElementById('quotationDescription');

    table.dataset.mode = mode;
    
    const editableCells = table.querySelectorAll('.edit-qty, .edit-unit, .edit-price, .edit-desc');
    editableCells.forEach(cell => {
        cell.contentEditable = (mode === 'edit');
    });

    descriptionBox.contentEditable = (mode === 'edit');

    if (mode === 'edit') {
        viewActions.style.display = 'none';
        editActions.style.display = 'flex';
    } else {
        viewActions.style.display = 'flex';
        editActions.style.display = 'none';
        if (originalData) {
            renderDetailedTable(originalData.detailed_resources);
            descriptionBox.innerText = originalData.description || '';
        }
    }
}

function renderDetailedTable(resources) {
    const tbody = document.querySelector('#detailedTable tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    
    // [수정] 공백을 제거한 정규화된 키를 사용하여 순서 정의
    const majorOrder = ['자재비', '인건비', '출장경비', '관리비'];
    const groups = groupByMajorThenMachine(resources);
    
    let html = '';
    let rowNo = 1;

    const renderSection = (majorKey) => {
        const machines = groups[majorKey];
        let majorTotal = 0; 
        
        // [수정] 매핑된 공식 타이틀 출력
        const displayTitle = MAJOR_DISPLAY_MAP[majorKey] || `${majorKey} 상세 내역`;
        html += `<tr class="section-title-row"><td colspan="8">■ ${displayTitle}</td></tr>`;
        
        Object.keys(machines).forEach(machineName => {
            const items = machines[machineName];
            const rowCount = items.length;

            items.forEach((item, idx) => {
                const subtotal = (item.compare || 0) * (item.solo_price || 0);
                majorTotal += subtotal;

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
                    <td class="edit-qty text-right">${item.compare}</td>
                    <td class="edit-unit text-center">${item.unit || '식'}</td>
                    <td class="edit-price text-right">${formatNumber(item.solo_price)}</td>
                    <td class="row-subtotal text-right">${formatNumber(subtotal)}</td>
                    <td class="edit-desc">${item.description || ''}</td>
                </tr>`;
            });
        });

        html += `
        <tr class="major-subtotal-row">
            <td colspan="6" class="text-center">${majorKey} 총 합계</td>
            <td class="text-right font-bold">${formatNumber(majorTotal)}</td>
            <td></td>
        </tr>`;
    };

    // 1. 정해진 순서대로 먼저 출력
    majorOrder.forEach(major => { if (groups[major]) renderSection(major); });
    
    // 2. [핵심] majorOrder에 없는 기타 카테고리도 누락 없이 출력
    Object.keys(groups).forEach(major => { 
        if (!majorOrder.includes(major)) renderSection(major); 
    });
    
    tbody.innerHTML = html;
    calculateGrandTotal();
}

// [핵심 수정] 그룹화 시 키에서 모든 공백을 제거하여 정규화 (Normalization)
function groupByMajorThenMachine(res) {
    return res.reduce((acc, curr) => {
        const rawMajor = curr.major || '기타';
        // "출장 경비"든 "출장경비"든 상관없이 "출장경비"로 통일하여 그룹화
        const major = rawMajor.replace(/\s/g, ''); 
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
                <td class="total-amount-cell text-right font-bold">${formatNumber(total)}</td>
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
        description: descriptionBox.innerText.trim(),
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

/**
 * 을지 엑셀 추출 (XLSX-Style 유지)
 */
function exportDetailedToExcel() {
    if (!originalData || !originalData.detailed_resources) return;

    const wb = XLSX.utils.book_new();
    const ws_data = [];
    const merges = [];

    // --- 1. 스타일 정의 ---
    const styleBase = { font: { name: "맑은 고딕", sz: 10 }, border: { top: { style: "thin" }, bottom: { style: "thin" }, left: { style: "thin" }, right: { style: "thin" } }, alignment: { vertical: "center" } };
    const styleTitle = { font: { bold: true, sz: 18 }, alignment: { horizontal: "center", vertical: "center" } };
    const styleHeader = { ...styleBase, fill: { fgColor: { rgb: "DBEAFE" } }, font: { bold: true }, alignment: { horizontal: "center" } };
    const styleCategory = { ...styleBase, fill: { fgColor: { rgb: "F3F4F6" } }, font: { bold: true } };
    const styleSubtotal = { ...styleBase, fill: { fgColor: { rgb: "FEF9C3" } }, font: { bold: true }, border: { top: { style: "thick" }, bottom: { style: "thick" } } };
    const styleNoteHead = { ...styleBase, fill: { fgColor: { rgb: "F8FAF6" } }, font: { bold: true }, alignment: { horizontal: "center" } };
    const styleNoteBox = { ...styleBase, alignment: { vertical: "top", wrapText: true } };

    // --- 2. 타이틀 및 테이블 헤더 ---
    ws_data.push([{ v: "상 세 견 적 서 (을 지)", s: styleTitle }]);
    merges.push({ s: { r: 0, c: 0 }, e: { r: 0, c: 8 } });

    const headers = ["No", "장비명", "품명", "규격", "수량", "단위", "단가", "공급가액", "비고"];
    ws_data.push(headers.map(v => ({ v, s: styleHeader })));

    // --- 3. 데이터 및 소계 렌더링 ---
    const groups = groupByMajorThenMachine(originalData.detailed_resources);
    const majorOrder = ["자재비", "인건비", "출장경비", "관리비"];
    let currentRow = 2;
    let globalNo = 1;
    let totalSum = 0;

    const renderExcelSection = (majorKey) => {
        if (!groups[majorKey]) return;

        const displayTitle = MAJOR_DISPLAY_MAP[majorKey] || `${majorKey} 상세 내역`;
        ws_data.push([{ v: `■ ${displayTitle}`, s: styleCategory }, "", "", "", "", "", "", "", ""]);
        merges.push({ s: { r: currentRow, c: 0 }, e: { r: currentRow, c: 8 } });
        currentRow++;

        const machines = groups[majorKey];
        let majorTotal = 0;

        Object.keys(machines).forEach(mName => {
            const items = machines[mName];
            const startMachineRow = currentRow;

            items.forEach(item => {
                const subtotal = (item.compare || 0) * (item.solo_price || 0);
                majorTotal += subtotal;
                totalSum += subtotal;

                ws_data.push([
                    { v: globalNo++, s: { ...styleBase, alignment: { horizontal: "center" } } },
                    { v: mName, s: styleBase },
                    { v: item.minor || "", s: styleBase },
                    { v: item.spec || "", s: styleBase },
                    { v: item.compare || 0, s: { ...styleBase, alignment: { horizontal: "center" } } },
                    { v: item.unit || "식", s: { ...styleBase, alignment: { horizontal: "center" } } },
                    { v: item.solo_price || 0, s: { ...styleBase, numFmt: "#,##0" } },
                    { v: subtotal, s: { ...styleBase, numFmt: "#,##0", font: { bold: true } } },
                    { v: item.description || "", s: styleBase }
                ]);
                currentRow++;
            });
            if (items.length > 1) merges.push({ s: { r: startMachineRow, c: 1 }, e: { r: currentRow - 1, c: 1 } });
        });

        const subRow = Array(9).fill(null).map(() => ({ v: "", s: styleSubtotal }));
        subRow[0] = { v: `${majorKey} 총 합계`, s: styleSubtotal };
        subRow[7] = { v: majorTotal, s: { ...styleSubtotal, numFmt: "#,##0" } };
        ws_data.push(subRow);
        merges.push({ s: { r: currentRow, c: 0 }, e: { r: currentRow, c: 6 } });
        currentRow++;
    };

    majorOrder.forEach(major => renderExcelSection(major));
    Object.keys(groups).forEach(major => { 
        if (!majorOrder.includes(major)) renderExcelSection(major); 
    });

    // --- 4. 최종 합계 ---
    const finalTotalRow = Array(9).fill(null).map(() => ({ v: "", s: { ...styleHeader, fill: { fgColor: { rgb: "FDE68A" } } } }));
    finalTotalRow[0] = { v: "합 계 (VAT 별도)", s: finalTotalRow[0].s };
    finalTotalRow[7] = { v: totalSum, s: { ...finalTotalRow[0].s, numFmt: "#,##0" } };
    ws_data.push(finalTotalRow);
    merges.push({ s: { r: currentRow, c: 0 }, e: { r: currentRow, c: 6 } });
    currentRow++;

    // --- 5. 비고 섹션 ---
    ws_data.push([]); currentRow++;
    ws_data.push([{ v: "비고 (Note)", s: styleNoteHead }, "", "", "", "", "", "", "", ""]);
    merges.push({ s: { r: currentRow, c: 0 }, e: { r: currentRow, c: 8 } });
    currentRow++;

    const noteContent = originalData.description || "특이사항 없음";
    ws_data.push([{ v: noteContent, s: styleNoteBox }, "", "", "", "", "", "", "", ""]);
    merges.push({ s: { r: currentRow, c: 0 }, e: { r: currentRow + 3, c: 8 } }); 

    const ws = XLSX.utils.aoa_to_sheet(ws_data);
    ws['!merges'] = merges;
    ws['!cols'] = [{ wch: 6 }, { wch: 18 }, { wch: 25 }, { wch: 20 }, { wch: 8 }, { wch: 8 }, { wch: 14 }, { wch: 15 }, { wch: 20 }];
    XLSX.utils.book_append_sheet(wb, ws, "을지");
    XLSX.writeFile(wb, `상세견적서_을지_${originalData.title || detailedId}.xlsx`);
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