/**
 * 내정가 견적 비교 상세 - 엑셀 하단 비고(Note) 포함 최종본
 */
let priceCompareId = null;
let priceCompareData = null;
let pageMode = 'view'; // view | edit

document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    pageMode = urlParams.get('mode') || 'view';
    
    const pathParts = window.location.pathname.split('/');
    priceCompareId = pathParts[pathParts.length - 1];
    
    if (priceCompareId) loadPriceCompareData(priceCompareId);

    setupCalculationEvents();
});

// ============================================================================
// 1. 데이터 로드
// ============================================================================
async function loadPriceCompareData(id) {
    const loading = document.getElementById('loading');
    try {
        if (loading) loading.style.display = 'block';
        const response = await fetch(`/api/v1/quotation/price_compare/${id}`);
        if (!response.ok) throw new Error('데이터 로드 실패');
        
        priceCompareData = await response.json();
        
        document.getElementById('creatorName').textContent = priceCompareData.creator || '-';
        document.getElementById('createdDate').textContent = priceCompareData.created_at?.substring(0, 10) || '-';
        
        initUIByMode();
        renderComparisonTable(priceCompareData.price_compare_resources);
        
        const sideMenu = document.getElementById('sideActionMenu');
        const notesSection = document.getElementById('notesSection');
        const footer = document.getElementById('actionFooter');

        if (sideMenu) sideMenu.style.display = (pageMode === 'edit') ? 'none' : 'flex';
        if (notesSection) notesSection.style.display = 'block';
        if (footer) footer.style.display = 'flex';

    } catch (error) {
        console.error('Load Error:', error);
    } finally {
        if (loading) loading.style.display = 'none';
    }
}

// ============================================================================
// 2. 모드 및 일괄 적용
// ============================================================================
function applyBulkUpperRate() {
    const bulkInput = document.getElementById('bulkUpperRate');
    if (!bulkInput) return;
    const rate = parseFloat(bulkInput.value) || 0;
    const rows = document.querySelectorAll('tr.category-row');
    rows.forEach(row => {
        const costPrice = parseNumber(row.querySelector('.cost-price').textContent);
        row.querySelector('.row-upper').textContent = rate;
        row.querySelector('.quote-price').textContent = formatNumber(Math.round(costPrice * (1 + rate / 100)));
    });
    calculateAllTotals();
}

function toggleEditMode(mode) {
    location.href = `?mode=${mode || 'edit'}`;
}

function initUIByMode() {
    const isEdit = (pageMode === 'edit');
    const footer = document.getElementById('actionFooter');
    const notes = document.getElementById('notesContent');
    const controls = document.getElementById('controlsContainer');
    const titleEl = document.getElementById('pageTitle');
    
    if (titleEl) titleEl.textContent = isEdit ? '내정가 견적가 비교 (수정)' : '내정가 견적가 비교 (조회)';
    
    if (notes) {
        notes.textContent = priceCompareData.description || '';
        notes.contentEditable = isEdit ? "true" : "false";
        if (isEdit) notes.classList.add('editable-cell');
        else notes.classList.remove('editable-cell');
    }

    if (controls) controls.style.display = isEdit ? 'flex' : 'none';

    if (isEdit) {
        footer.innerHTML = `
            <button class="btn btn-secondary btn-lg" onclick="location.href='?mode=view'">취소</button>
            <button class="btn btn-primary btn-lg" onclick="saveChanges()">변경사항 저장</button>`;
    } else {
        footer.innerHTML = `
            <button class="btn btn-secondary btn-lg" onclick="window.history.back()">목록으로</button>
            <button class="btn btn-warning btn-lg" onclick="toggleEditMode('edit')">수정하기</button>
            <button class="btn btn-outline btn-lg" onclick="exportToExcel()">Excel 저장</button>
            <button class="btn btn-outline btn-lg" onclick="createDetailedFromCompare()">📑 을지 만들기</button>
            <button class="btn btn-primary btn-lg" onclick="createHeaderFromCompare()">📄 갑지 만들기</button>`;
    }
}

// ============================================================================
// 3. 테이블 렌더링 & 계산
// ============================================================================
function renderComparisonTable(resources) {
    const tbody = document.getElementById('comparisonTableBody');
    if (!tbody) return;
    const isEdit = (pageMode === 'edit');
    tbody.innerHTML = '';

    const groups = groupByMajorThenMachine(resources);
    const majorOrder = ["자재비", "인건비", "경비", "관리비"];
    const sortedMajors = Object.keys(groups).sort((a, b) => (majorOrder.indexOf(a) === -1 ? 99 : majorOrder.indexOf(a)) - (majorOrder.indexOf(b) === -1 ? 99 : majorOrder.indexOf(b)));

    let html = '';
    sortedMajors.forEach(major => {
        const machineGroups = groups[major];
        let majorRowCount = Object.values(machineGroups).reduce((acc, curr) => acc + curr.length, 0) + 1;
        let isFirstMajorRow = true;
        Object.keys(machineGroups).forEach(machineName => {
            const items = machineGroups[machineName];
            items.forEach((item, idx) => {
                html += `<tr class="category-row" data-major="${major}" data-machine-id="${item.machine_id}" data-machine-name="${machineName}">`;
                if (isFirstMajorRow) { html += `<td rowspan="${majorRowCount}" class="category-cell"><strong>${major}</strong></td>`; isFirstMajorRow = false; }
                if (idx === 0) html += `<td rowspan="${items.length}" class="machine-name-cell"><strong>${machineName}</strong></td>`;
                html += `
                    <td class="minor-name">${item.minor || ''}</td>
                    <td class="cost-qty">${item.cost_compare || 0}</td>
                    <td>식</td>
                    <td class="cost-price">${formatNumber(item.cost_solo_price)}</td>
                    <td class="cost-amount">0</td>
                    <td class="quote-qty ${isEdit ? 'editable-cell' : ''}" ${isEdit ? 'contenteditable="true"' : ''}>${item.quotation_compare || 0}</td>
                    <td>식</td>
                    <td class="quote-price ${isEdit ? 'editable-cell' : ''}" ${isEdit ? 'contenteditable="true"' : ''}>${formatNumber(item.quotation_solo_price)}</td>
                    <td class="row-upper ${isEdit ? 'editable-cell' : ''}" ${isEdit ? 'contenteditable="true"' : ''}>${item.upper || 0}</td>
                    <td class="quote-amount">0</td>
                    <td class="row-note ${isEdit ? 'editable-cell' : ''}" ${isEdit ? 'contenteditable="true"' : ''}>${item.description || ''}</td>
                </tr>`;
            });
        });
        html += `<tr class="subtotal-row" data-subtotal-major="${major}"><td colspan="2">${major} 소계</td><td colspan="3"></td><td class="cost-subtotal">0</td><td colspan="4"></td><td class="quote-subtotal">0</td><td class="difference-cell">0</td></tr>`;
    });
    html += `<tr class="final-total-row"><td colspan="6">TOTAL</td><td class="cost-final-total">0</td><td colspan="4"></td><td class="final-total-cell quote-final-total">0</td><td class="difference-cell">0</td></tr>
             <tr class="markup-row"><td colspan="11"></td><td class="margin-cell">0 %</td><td class="markup-cell">이익률</td></tr>`;
    tbody.innerHTML = html;
    calculateAllTotals();
}

async function saveChanges() {
    if (!priceCompareId || !priceCompareData) return;
    if (!confirm('현재 수정된 내용을 저장하시겠습니까?')) return;
    const resources = [];
    document.querySelectorAll('tr.category-row').forEach(row => {
        resources.push({
            "machine_id": row.dataset.machineId, "machine_name": row.dataset.machineName, "major": row.dataset.major,
            "minor": row.querySelector('.minor-name')?.textContent.trim(),
            "cost_solo_price": parseNumber(row.querySelector('.cost-price')?.textContent), "cost_unit": "식", "cost_compare": parseNumber(row.querySelector('.cost-qty')?.textContent),
            "quotation_solo_price": parseNumber(row.querySelector('.quote-price')?.textContent), "quotation_unit": "식", "quotation_compare": parseNumber(row.querySelector('.quote-qty')?.textContent),
            "upper": parseFloat(row.querySelector('.row-upper')?.textContent) || 0, "description": row.querySelector('.row-note')?.textContent.trim() || ""
        });
    });
    const payload = { "creator": document.getElementById('creatorName').textContent.trim(), "description": document.getElementById('notesContent').textContent.trim(), "machine_ids": priceCompareData.machine_ids, "price_compare_resources": resources };
    const res = await fetch(`/api/v1/quotation/price_compare/${priceCompareId}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    if (res.ok) { alert('저장되었습니다.'); location.href = '?mode=view'; }
}

// ============================================================================
// 4. [수정] 엑셀 다운로드 (하단 비고란 추가 완료)
// ============================================================================
function exportToExcel() {
    if (!priceCompareData || !priceCompareData.price_compare_resources) return;

    const wb = XLSX.utils.book_new();
    const ws_data = [];
    const merges = [];

    const styleBase = { font: { name: "맑은 고딕", sz: 10 }, border: { top: { style: "thin" }, bottom: { style: "thin" }, left: { style: "thin" }, right: { style: "thin" } }, alignment: { vertical: "center" } };
    const styleTitle = { font: { bold: true, sz: 18 }, alignment: { horizontal: "center", vertical: "center" } };
    const styleHeader = { ...styleBase, fill: { fgColor: { rgb: "DBEAFE" } }, font: { bold: true, sz: 10 }, alignment: { horizontal: "center" } };
    const styleSubtotal = { ...styleBase, fill: { fgColor: { rgb: "FEF9C3" } }, font: { bold: true }, border: { top: { style: "thick" }, bottom: { style: "thick" } } };
    const styleFinalTotal = { ...styleBase, fill: { fgColor: { rgb: "FDE68A" } }, font: { bold: true }, border: { top: { style: "double" }, bottom: { style: "thick" } } };
    const styleNoteHead = { ...styleBase, fill: { fgColor: { rgb: "F2F2F2" } }, font: { bold: true }, alignment: { horizontal: "center" } };
    const styleNoteBox = { ...styleBase, alignment: { vertical: "top", wrapText: true } };

    ws_data.push([{ v: "내 정 가 / 견 적 가 비 교 서", s: styleTitle }]);
    merges.push({ s: { r: 0, c: 0 }, e: { r: 0, c: 12 } });

    const h1 = ["항목", "장비명", "구분", "내정가", "", "", "", "견적가", "", "", "", "", "비고"].map(v => ({ v, s: styleHeader }));
    ws_data.push(h1);
    const h2 = ["", "", "", "수량", "단위", "단가", "금액", "수량", "단위", "단가", "상승률", "금액", ""].map(v => ({ v, s: styleHeader }));
    ws_data.push(h2);
    merges.push({ s: { r: 1, c: 3 }, e: { r: 1, c: 6 } }, { s: { r: 1, c: 7 }, e: { r: 1, c: 11 } });
    [0, 1, 2, 12].forEach(c => merges.push({ s: { r: 1, c }, e: { r: 2, c } }));

    const groups = groupByMajorThenMachine(priceCompareData.price_compare_resources);
    const majorOrder = ["자재비", "인건비", "경비", "관리비"];
    const sortedMajors = Object.keys(groups).sort((a, b) => (majorOrder.indexOf(a) === -1 ? 99 : majorOrder.indexOf(a)) - (majorOrder.indexOf(b) === -1 ? 99 : majorOrder.indexOf(b)));

    let currentRow = 3;
    let grandCostTotal = 0, grandQuoteTotal = 0;

    sortedMajors.forEach(major => {
        const mGroups = groups[major];
        const startMajorRow = currentRow;
        let majorCost = 0, majorQuote = 0;
        Object.keys(mGroups).forEach(mName => {
            const items = mGroups[mName];
            const startMachineRow = currentRow;
            items.forEach((item, idx) => {
                const cAmt = (item.cost_compare || 0) * (item.cost_solo_price || 0);
                const qAmt = (item.quotation_compare || 0) * (item.quotation_solo_price || 0);
                majorCost += cAmt; majorQuote += qAmt;
                ws_data.push([
                    { v: idx === 0 && startMajorRow === currentRow ? major : "", s: styleBase },
                    { v: idx === 0 ? mName : "", s: styleBase },
                    { v: item.minor || "", s: styleBase },
                    { v: item.cost_compare || 0, s: styleBase }, { v: "식", s: styleBase },
                    { v: item.cost_solo_price || 0, s: { ...styleBase, numFmt: "#,##0" } }, { v: cAmt, s: { ...styleBase, numFmt: "#,##0" } },
                    { v: item.quotation_compare || 0, s: styleBase }, { v: "식", s: styleBase },
                    { v: item.quotation_solo_price || 0, s: { ...styleBase, numFmt: "#,##0" } },
                    { v: (item.upper || 0) + "%", s: { ...styleBase, font: { color: { rgb: "DC2626" } } } },
                    { v: qAmt, s: { ...styleBase, numFmt: "#,##0", font: { bold: true } } }, { v: item.description || "", s: styleBase }
                ]);
                currentRow++;
            });
            if (items.length > 1) merges.push({ s: { r: startMachineRow, c: 1 }, e: { r: currentRow - 1, c: 1 } });
        });
        const subRow = Array(13).fill(null).map(() => ({ v: "", s: styleSubtotal }));
        subRow[0] = { v: `${major} 소계`, s: styleSubtotal }; subRow[6] = { v: majorCost, s: { ...styleSubtotal, numFmt: "#,##0" } }; subRow[11] = { v: majorQuote, s: { ...styleSubtotal, numFmt: "#,##0" } };
        subRow[12] = { v: majorQuote - majorCost, s: { ...styleSubtotal, numFmt: "#,##0" } };
        ws_data.push(subRow);
        merges.push({ s: { r: startMajorRow, c: 0 }, e: { r: currentRow, c: 0 } }, { s: { r: currentRow, c: 0 }, e: { r: currentRow, c: 2 } });
        grandCostTotal += majorCost; grandQuoteTotal += majorQuote; currentRow++;
    });

    const totalRow = Array(13).fill(null).map(() => ({ v: "", s: styleFinalTotal }));
    totalRow[0] = { v: "GRAND TOTAL", s: styleFinalTotal }; totalRow[6] = { v: grandCostTotal, s: { ...styleFinalTotal, numFmt: "#,##0" } }; totalRow[11] = { v: grandQuoteTotal, s: { ...styleFinalTotal, numFmt: "#,##0" } };
    totalRow[12] = { v: grandQuoteTotal - grandCostTotal, s: { ...styleFinalTotal, numFmt: "#,##0" } };
    ws_data.push(totalRow);
    merges.push({ s: { r: currentRow, c: 0 }, e: { r: currentRow, c: 5 } }); currentRow++;

    // --- [추가] 비고 섹션 (Note) ---
    ws_data.push([]); currentRow++; // 빈 줄
    ws_data.push([{ v: "비 고 ( Note )", s: styleNoteHead }, "", "", "", "", "", "", "", "", "", "", "", ""]);
    merges.push({ s: { r: currentRow, c: 0 }, e: { r: currentRow, c: 12 } }); currentRow++;
    ws_data.push([{ v: priceCompareData.description || "특이사항 없음", s: styleNoteBox }, "", "", "", "", "", "", "", "", "", "", "", ""]);
    merges.push({ s: { r: currentRow, c: 0 }, e: { r: currentRow + 3, c: 12 } }); // 내용 박스 확보

    const ws = XLSX.utils.aoa_to_sheet(ws_data);
    ws['!merges'] = merges;
    ws['!cols'] = [{ wch: 12 }, { wch: 18 }, { wch: 25 }, { wch: 6 }, { wch: 6 }, { wch: 14 }, { wch: 15 }, { wch: 6 }, { wch: 6 }, { wch: 14 }, { wch: 8 }, { wch: 15 }, { wch: 20 }];
    XLSX.utils.book_append_sheet(wb, ws, "내정가비교");
    XLSX.writeFile(wb, `내정가견적비교서_${priceCompareData.description?.substring(0,10) || priceCompareId}.xlsx`);
}

// 유틸리티
function setupCalculationEvents() {
    const tbody = document.getElementById('comparisonTableBody');
    if (!tbody) return;
    tbody.addEventListener('input', (e) => {
        const row = e.target.closest('tr'); if (!row?.classList.contains('category-row')) return;
        if (e.target.classList.contains('row-upper')) {
            const costP = parseNumber(row.querySelector('.cost-price').textContent);
            const rate = parseFloat(e.target.textContent) || 0;
            row.querySelector('.quote-price').textContent = formatNumber(Math.round(costP * (1 + rate / 100)));
        } else if (e.target.classList.contains('quote-price')) {
            const costP = parseNumber(row.querySelector('.cost-price').textContent);
            const quoteP = parseNumber(e.target.textContent);
            if (costP > 0) row.querySelector('.row-upper').textContent = ((quoteP - costP) / costP * 100).toFixed(1);
        }
        calculateAllTotals();
    });
}
function calculateAllTotals() {
    let tCost = 0, tQuote = 0; const majorTotals = {};
    document.querySelectorAll('tr.category-row').forEach(row => {
        const major = row.dataset.major; if (!majorTotals[major]) majorTotals[major] = { c: 0, q: 0 };
        const cp = parseNumber(row.querySelector('.cost-price').textContent), cq = parseNumber(row.querySelector('.cost-qty').textContent);
        const qp = parseNumber(row.querySelector('.quote-price').textContent), qq = parseNumber(row.querySelector('.quote-qty').textContent);
        const camt = cp * cq, qamt = qp * qq;
        row.querySelector('.cost-amount').textContent = formatNumber(camt); row.querySelector('.quote-amount').textContent = formatNumber(qamt);
        majorTotals[major].c += camt; majorTotals[major].q += qamt;
    });
    document.querySelectorAll('.subtotal-row').forEach(row => {
        const t = majorTotals[row.dataset.subtotalMajor] || { c: 0, q: 0 };
        row.querySelector('.cost-subtotal').textContent = formatNumber(t.c); row.querySelector('.quote-subtotal').textContent = formatNumber(t.q);
        row.querySelector('.difference-cell').textContent = formatNumber(t.q - t.c);
        tCost += t.c; tQuote += t.q;
    });
    const fr = document.querySelector('.final-total-row');
    if (fr) { fr.querySelector('.cost-final-total').textContent = formatNumber(tCost); fr.querySelector('.quote-final-total').textContent = formatNumber(tQuote); fr.querySelector('.difference-cell').textContent = formatNumber(tQuote - tCost); }
    const mr = document.querySelector('.markup-row');
    if (mr && tQuote > 0) mr.querySelector('.margin-cell').textContent = (((tQuote - tCost) / tQuote) * 100).toFixed(1) + ' %';
}
function createDetailedFromCompare() { location.href = `/service/quotation/general/detailed/register?general_id=${priceCompareData.general_id}&compare_id=${priceCompareId}`; }
function createHeaderFromCompare() { location.href = `/service/quotation/general/header/register?general_id=${priceCompareData.general_id}&compare_id=${priceCompareId}`; }
function groupByMajorThenMachine(res) { const g = {}; res.forEach(i => { const maj = i.major || '기타', mach = i.machine_name || '미분류'; if (!g[maj]) g[maj] = {}; if (!g[maj][mach]) g[maj][mach] = []; g[maj][mach].push(i); }); return g; }
function formatNumber(n) { return (n || 0).toLocaleString('ko-KR'); }
function parseNumber(s) { return parseInt(s?.toString().replace(/[^0-9.-]/g, '')) || 0; }