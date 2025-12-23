/**
 * 내정가 견적 비교 상세 - 저장 로직 보완 및 자동 생성 기능 포함 전체본
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

    // 테이블 내 실시간 계산 이벤트
    setupCalculationEvents();
});

// ============================================================================
// 1. 데이터 로드 및 초기화
// ============================================================================

async function loadPriceCompareData(id) {
    const loading = document.getElementById('loading');
    try {
        loading.style.display = 'block';
        const response = await fetch(`/api/v1/quotation/price_compare/${id}`);
        if (!response.ok) throw new Error('데이터 로드 실패');
        
        priceCompareData = await response.json();
        
        document.getElementById('creatorName').textContent = priceCompareData.creator || '-';
        document.getElementById('createdDate').textContent = priceCompareData.created_at?.substring(0, 10) || '-';
        
        initUIByMode();
        renderComparisonTable(priceCompareData.price_compare_resources);
        
        document.getElementById('sideActionMenu').style.display = 'flex';
        document.getElementById('controlsContainer').style.display = 'flex';
        document.getElementById('notesSection').style.display = 'block';
        document.getElementById('actionFooter').style.display = 'flex';
    } catch (error) {
        console.error(error);
        alert('로딩 실패: ' + error.message);
    } finally {
        loading.style.display = 'none';
    }
}

// ============================================================================
// 2. [핵심] 저장 기능 (보완 완료)
// ============================================================================

async function saveChanges() {
    if (!priceCompareId || !priceCompareData) return;
    if (!confirm('현재 수정된 내용을 저장하시겠습니까?')) return;

    const rows = document.querySelectorAll('tr.category-row');
    const resources = [];
    
    try {
        rows.forEach(row => {
            // 데이터 속성 및 셀 텍스트로부터 정보 수집
            resources.push({
                "machine_id": row.dataset.machineId,
                "machine_name": row.dataset.machineName,
                "major": row.dataset.major,
                "minor": row.querySelector('.minor-name')?.textContent.trim(),
                "cost_solo_price": parseNumber(row.querySelector('.cost-price')?.textContent),
                "cost_unit": "식",
                "cost_compare": parseNumber(row.querySelector('.cost-qty')?.textContent),
                "quotation_solo_price": parseNumber(row.querySelector('.quote-price')?.textContent),
                "quotation_unit": "식",
                "quotation_compare": parseNumber(row.querySelector('.quote-qty')?.textContent),
                "upper": parseFloat(row.querySelector('.row-upper')?.textContent) || 0,
                "description": row.querySelector('.row-note')?.textContent.trim() || ""
            });
        });

        const payload = {
            "creator": document.getElementById('creatorName').textContent.trim(),
            "description": document.getElementById('notesContent').textContent.trim(),
            "machine_ids": priceCompareData.machine_ids, // 기존 ID 리스트 유지
            "price_compare_resources": resources
        };

        const res = await fetch(`/api/v1/quotation/price_compare/${priceCompareId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (res.ok) {
            alert('성공적으로 저장되었습니다.');
            location.href = '?mode=view'; // 저장 후 조회 모드로 전환
        } else {
            const err = await res.json();
            alert('저장 실패: ' + (err.detail || '서버 오류가 발생했습니다.'));
        }
    } catch (e) {
        console.error('Save Error:', e);
        alert('통신 중 오류가 발생했습니다.');
    }
}

// ============================================================================
// 3. 페이지 이동 및 생성 기능
// ============================================================================

function createDetailedFromCompare() {
    if (!priceCompareData?.general_id) return alert('일반 견적서 정보를 찾을 수 없습니다.');
    location.href = `/service/quotation/general/detailed/register?general_id=${priceCompareData.general_id}&compare_id=${priceCompareId}`;
}

function createHeaderFromCompare() {
    if (!priceCompareData?.general_id) return alert('일반 견적서 정보를 찾을 수 없습니다.');
    location.href = `/service/quotation/general/header/register?general_id=${priceCompareData.general_id}&compare_id=${priceCompareId}`;
}

// ============================================================================
// 4. 테이블 렌더링 및 UI 설정
// ============================================================================

function renderComparisonTable(resources) {
    const tbody = document.getElementById('comparisonTableBody');
    const isEdit = (pageMode === 'edit');
    tbody.innerHTML = '';

    const groups = groupByMajorThenMachine(resources);
    let html = '';

    Object.keys(groups).forEach(major => {
        const machineGroups = groups[major];
        let majorRowCount = Object.values(machineGroups).reduce((acc, curr) => acc + curr.length, 0) + 1;
        let isFirstMajorRow = true;
        
        Object.keys(machineGroups).forEach(machineName => {
            const items = machineGroups[machineName];
            items.forEach((item, idx) => {
                html += `<tr class="category-row" data-major="${major}" data-machine-id="${item.machine_id}" data-machine-name="${machineName}">`;
                if (isFirstMajorRow) {
                    html += `<td rowspan="${majorRowCount}" class="category-cell"><strong>${major}</strong></td>`;
                    isFirstMajorRow = false;
                }
                if (idx === 0) html += `<td rowspan="${items.length}" class="machine-name-cell"><strong>${machineName}</strong></td>`;
                
                html += `<td class="minor-name">${item.minor || ''}</td>
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

function initUIByMode() {
    const isEdit = (pageMode === 'edit');
    const footer = document.getElementById('actionFooter');
    const sideMenu = document.getElementById('sideActionMenu');
    const notes = document.getElementById('notesContent');
    
    document.getElementById('pageTitle').textContent = isEdit ? '내정가 견적가 비교 (수정)' : '내정가 견적가 비교 (조회)';
    notes.textContent = priceCompareData.description || '';

    if (isEdit) {
        notes.contentEditable = "true";
        notes.classList.add('editable-cell');
        if (sideMenu) sideMenu.style.display = 'none';
        footer.innerHTML = `<button class="btn btn-secondary btn-lg" onclick="location.href='?mode=view'">취소</button>
                            <button class="btn btn-primary btn-lg" onclick="saveChanges()">변경사항 저장</button>`;
    } else {
        notes.contentEditable = "false";
        if (sideMenu) sideMenu.style.display = 'flex';
        footer.innerHTML = `<button class="btn btn-secondary btn-lg" onclick="window.history.back()">목록으로</button>
                            <button class="btn btn-outline btn-lg" onclick="createDetailedFromCompare()">📑 을지 만들기</button>
                            <button class="btn btn-primary btn-lg" onclick="createHeaderFromCompare()">📄 갑지 만들기</button>`;
    }
}

// ============================================================================
// 5. 계산 및 유틸리티
// ============================================================================

function setupCalculationEvents() {
    const tbody = document.getElementById('comparisonTableBody');
    if (!tbody) return;
    tbody.addEventListener('input', (e) => {
        const row = e.target.closest('tr');
        if (!row?.classList.contains('category-row')) return;

        // 상승률 수정 시 단가 계산
        if (e.target.classList.contains('row-upper')) {
            const costP = parseNumber(row.querySelector('.cost-price').textContent);
            const rate = parseFloat(e.target.textContent) || 0;
            row.querySelector('.quote-price').textContent = formatNumber(Math.round(costP * (1 + rate / 100)));
        } 
        // 단가 직접 수정 시 상승률 역계산
        else if (e.target.classList.contains('quote-price')) {
            const costP = parseNumber(row.querySelector('.cost-price').textContent);
            const quoteP = parseNumber(e.target.textContent);
            if (costP > 0) row.querySelector('.row-upper').textContent = ((quoteP - costP) / costP * 100).toFixed(1);
        }
        calculateAllTotals();
    });
}

function calculateAllTotals() {
    const rows = document.querySelectorAll('tr.category-row');
    let totalCost = 0, totalQuote = 0;
    const majorTotals = {};

    rows.forEach(row => {
        const major = row.dataset.major;
        if (!majorTotals[major]) majorTotals[major] = { c: 0, q: 0 };

        const cp = parseNumber(row.querySelector('.cost-price').textContent);
        const cq = parseNumber(row.querySelector('.cost-qty').textContent);
        const qp = parseNumber(row.querySelector('.quote-price').textContent);
        const qq = parseNumber(row.querySelector('.quote-qty').textContent);

        const camt = cp * cq;
        const qamt = qp * qq;

        row.querySelector('.cost-amount').textContent = formatNumber(camt);
        row.querySelector('.quote-amount').textContent = formatNumber(qamt);

        majorTotals[major].c += camt;
        majorTotals[major].q += qamt;
    });

    document.querySelectorAll('.subtotal-row').forEach(row => {
        const major = row.dataset.subtotalMajor;
        const t = majorTotals[major] || { c: 0, q: 0 };
        row.querySelector('.cost-subtotal').textContent = formatNumber(t.c);
        row.querySelector('.quote-subtotal').textContent = formatNumber(t.q);
        row.querySelector('.difference-cell').textContent = formatNumber(t.q - t.c);
        totalCost += t.c; totalQuote += t.q;
    });

    const fr = document.querySelector('.final-total-row');
    if (fr) {
        fr.querySelector('.cost-final-total').textContent = formatNumber(totalCost);
        fr.querySelector('.quote-final-total').textContent = formatNumber(totalQuote);
        fr.querySelector('.difference-cell').textContent = formatNumber(totalQuote - totalCost);
    }

    const mr = document.querySelector('.markup-row');
    if (mr && totalQuote > 0) {
        mr.querySelector('.margin-cell').textContent = (((totalQuote - totalCost) / totalQuote) * 100).toFixed(1) + ' %';
    }
}

function groupByMajorThenMachine(res) {
    const g = {};
    res.forEach(i => {
        const maj = i.major || '기타', mach = i.machine_name || '미분류';
        if (!g[maj]) g[maj] = {};
        if (!g[maj][mach]) g[maj][mach] = [];
        g[maj][mach].push(i);
    });
    return g;
}

function formatNumber(n) { return (n || 0).toLocaleString('ko-KR'); }
function parseNumber(s) { return parseInt(s?.toString().replace(/[^0-9.-]/g, '')) || 0; }
function toggleEditMode() { location.href = '?mode=edit'; }