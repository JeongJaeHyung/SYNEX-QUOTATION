/**
 * 내정가 견적가 비교 상세 페이지 - 장비명별 그룹화
 * (machine_name 기준으로 묶어서 표시, rowspan 적용)
 */

let priceCompareId = null;
let priceCompareData = null;
let pageMode = 'view'; // view | edit

// ============================================================================
// 페이지 초기화
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    pageMode = urlParams.get('mode') || 'view';
    
    const pathParts = window.location.pathname.split('/');
    priceCompareId = pathParts[pathParts.length - 1];
    
    if (priceCompareId) {
        loadPriceCompareData(priceCompareId);
    }

    // 상단 일괄 상승률 입력
    const globalMarkupInput = document.getElementById('markup-rate');
    if (globalMarkupInput) {
        globalMarkupInput.addEventListener('input', function() {
            const rate = parseFloat(this.value) || 0;
            recalculateAllByGlobalRate(rate);
        });
    }

    // 테이블 내 실시간 계산
    const tbody = document.getElementById('comparisonTableBody');
    if (tbody) {
        tbody.addEventListener('input', function(e) {
            if (!e.target.hasAttribute('contenteditable')) return;

            const row = e.target.closest('tr');
            if (row.classList.contains('category-row')) {
                // 행별 상승률 수정 시
                if (e.target.classList.contains('row-upper')) {
                    const costPrice = parseNumber(row.querySelector('.cost-price').textContent);
                    const rowRate = parseFloat(e.target.textContent) || 0;
                    const newQuotePrice = Math.round(costPrice * (1 + rowRate / 100));
                    row.querySelector('.quote-price').textContent = formatNumber(newQuotePrice);
                } 
                // 견적 단가 직접 수정 시
                else if (e.target.classList.contains('quote-price')) {
                    const costPrice = parseNumber(row.querySelector('.cost-price').textContent);
                    const quotePrice = parseNumber(e.target.textContent);
                    if (costPrice > 0) {
                        const newUpper = ((quotePrice - costPrice) / costPrice * 100).toFixed(1);
                        row.querySelector('.row-upper').textContent = newUpper;
                    }
                }
            }
            calculateAllTotals();
        });
    }
});

// ============================================================================
// 데이터 로드
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
// 테이블 렌더링 - 장비명별 그룹화
// ============================================================================

function renderComparisonTable(resources) {
    const tbody = document.getElementById('comparisonTableBody');
    const isEdit = (pageMode === 'edit');
    tbody.innerHTML = '';

    // 1. major(항목) 먼저 그룹화, 그 안에서 machine_name으로 그룹화
    const groups = groupByMajorThenMachine(resources);
    
    let html = '';

    // 2. major(항목)별로 순회
    Object.keys(groups).forEach(major => {
        const machineGroups = groups[major];
        let majorRowCount = 0;
        
        // major 내 전체 행 개수 계산 (데이터 행 + 소계 행)
        Object.keys(machineGroups).forEach(machineName => {
            majorRowCount += machineGroups[machineName].length; // 데이터 행
        });
        majorRowCount += 1; // major 소계 행
        
        let isFirstMajorRow = true;
        
        // 3. 각 장비명별로 순회
        Object.keys(machineGroups).forEach(machineName => {
            const items = machineGroups[machineName];
            
            items.forEach((item, idx) => {
                html += `<tr class="category-row" data-major="${major}" data-machine-name="${machineName}" data-machine-id="${item.machine_id}">`;
                
                // 항목(major) 셀 (첫 번째 행에만 rowspan 적용)
                if (isFirstMajorRow) {
                    html += `<td rowspan="${majorRowCount}" class="category-cell"><strong>${major}</strong></td>`;
                    isFirstMajorRow = false;
                }
                
                // 장비명 셀 (각 장비의 첫 행에만 rowspan 적용)
                if (idx === 0) {
                    html += `<td rowspan="${items.length}" class="machine-name-cell"><strong>${machineName || '미분류'}</strong></td>`;
                }
                
                // 구분(minor)
                html += `<td class="minor-name">${item.minor || ''}</td>`;
                
                // 내정가
                html += `<td class="cost-qty">${item.cost_compare || 0}</td>`;
                html += `<td>${item.cost_unit || '식'}</td>`;
                html += `<td class="cost-price">${formatNumber(item.cost_solo_price)}</td>`;
                html += `<td class="cost-amount">0</td>`;

                // 견적가
                html += `<td class="quote-qty ${isEdit ? 'editable-cell' : ''}" ${isEdit ? 'contenteditable="true"' : ''}>${item.quotation_compare || 0}</td>`;
                html += `<td>${item.quotation_unit || '식'}</td>`;
                html += `<td class="quote-price ${isEdit ? 'editable-cell' : ''}" ${isEdit ? 'contenteditable="true"' : ''}>${formatNumber(item.quotation_solo_price)}</td>`;
                html += `<td class="row-upper ${isEdit ? 'editable-cell' : ''}" ${isEdit ? 'contenteditable="true"' : ''}>${item.upper || 0}</td>`;
                html += `<td class="quote-amount">0</td>`;
                
                // 비고
                html += `<td class="row-note ${isEdit ? 'editable-cell' : ''}" ${isEdit ? 'contenteditable="true"' : ''}>${item.description || ''}</td>`;
                html += `</tr>`;
            });
        });

        // major 소계 행
        html += `<tr class="subtotal-row" data-subtotal-major="${major}">
                    <td colspan="2">${major} 소계</td>
                    <td colspan="3"></td><td class="subtotal-cell cost-subtotal">0</td>
                    <td colspan="4"></td><td class="subtotal-cell quote-subtotal">0</td>
                    <td class="difference-cell">0</td>
                 </tr>`;
    });

    // 4. 요약 행 (Sub Total, 관리비, TOTAL, 이익률)
    html += renderSummaryRows(isEdit);

    tbody.innerHTML = html;
    calculateAllTotals();
}

// major(항목) 먼저 그룹화, 그 안에서 machine_name으로 그룹화
function groupByMajorThenMachine(resources) {
    const grouped = {};
    
    resources.forEach(item => {
        const major = item.major || '기타';
        const machineName = item.machine_name || '미분류';
        
        if (!grouped[major]) {
            grouped[major] = {};
        }
        if (!grouped[major][machineName]) {
            grouped[major][machineName] = [];
        }
        grouped[major][machineName].push(item);
    });
    
    return grouped;
}

// 요약 행 렌더링
function renderSummaryRows(isEdit) {
    let html = '';
    
    html += `<tr class="total-row">
                <td colspan="6">Sub Total</td>
                <td class="total-cell cost-total">0</td>
                <td colspan="4"></td>
                <td class="total-cell quote-total">0</td>
                <td class="difference-cell">0</td>
             </tr>`;
    
    html += `<tr class="management-row">
                <td rowspan="2" colspan="2" class="category-cell">관리비</td>
                <td>일반관리비</td>
                <td colspan="4"></td>
                <td class="mgmt-rate ${isEdit ? 'editable-cell' : ''}" ${isEdit ? 'contenteditable="true"' : ''}>6</td>
                <td colspan="3"></td>
                <td class="mgmt-amount">0</td>
                <td></td>
             </tr>`;
    
    html += `<tr class="management-row">
                <td>기업이윤</td>
                <td colspan="4"></td>
                <td class="profit-rate ${isEdit ? 'editable-cell' : ''}" ${isEdit ? 'contenteditable="true"' : ''}>4</td>
                <td colspan="3"></td>
                <td class="profit-amount">0</td>
                <td></td>
             </tr>`;
    
    html += `<tr class="final-total-row">
                <td colspan="6">TOTAL</td>
                <td class="final-total-cell cost-final-total">0</td>
                <td colspan="4"></td>
                <td class="final-total-cell quote-final-total">0</td>
                <td class="difference-cell">0</td>
             </tr>`;
    
    html += `<tr class="markup-row">
                <td colspan="11"></td>
                <td class="margin-cell">0 %</td>
                <td class="markup-cell">이익률</td>
             </tr>`;
    
    return html;
}

// ============================================================================
// 계산 로직
// ============================================================================

function calculateAllTotals() {
    const rows = document.querySelectorAll('tr.category-row');
    let totalCost = 0, totalQuote = 0;
    const majorTotals = {};

    // 1. 행별 금액 계산 및 major별 집계
    rows.forEach(row => {
        const major = row.dataset.major;
        
        if (!majorTotals[major]) {
            majorTotals[major] = { c: 0, q: 0 };
        }

        const cq = parseNumber(row.querySelector('.cost-qty')?.textContent);
        const cp = parseNumber(row.querySelector('.cost-price')?.textContent);
        const qq = parseNumber(row.querySelector('.quote-qty')?.textContent);
        const qp = parseNumber(row.querySelector('.quote-price')?.textContent);

        const camt = cq * cp;
        const qamt = qq * qp;

        row.querySelector('.cost-amount').textContent = formatNumber(camt);
        row.querySelector('.quote-amount').textContent = formatNumber(qamt);

        majorTotals[major].c += camt;
        majorTotals[major].q += qamt;
    });

    // 2. major별 소계 업데이트
    document.querySelectorAll('.subtotal-row').forEach(row => {
        const major = row.dataset.subtotalMajor;
        const totals = majorTotals[major] || { c: 0, q: 0 };
        
        row.querySelector('.cost-subtotal').textContent = formatNumber(totals.c);
        row.querySelector('.quote-subtotal').textContent = formatNumber(totals.q);
        row.querySelector('.difference-cell').textContent = formatNumber(totals.q - totals.c);
        
        totalCost += totals.c;
        totalQuote += totals.q;
    });

    // 3. Sub Total
    const tr = document.querySelector('.total-row');
    if (tr) {
        tr.querySelector('.cost-total').textContent = formatNumber(totalCost);
        tr.querySelector('.quote-total').textContent = formatNumber(totalQuote);
        tr.querySelector('.difference-cell').textContent = formatNumber(totalQuote - totalCost);
    }

    // 4. 관리비
    let mgmtSum = 0;
    document.querySelectorAll('.management-row').forEach(row => {
        const rateCell = row.querySelector('.mgmt-rate, .profit-rate');
        const amountCell = row.querySelector('.mgmt-amount, .profit-amount');
        if (rateCell && amountCell) {
            const rate = parseFloat(rateCell.textContent) || 0;
            const amt = Math.round(totalQuote * (rate / 100));
            amountCell.textContent = formatNumber(amt);
            mgmtSum += amt;
        }
    });

    // 5. 최종 TOTAL
    const finalQ = totalQuote + mgmtSum;
    const fr = document.querySelector('.final-total-row');
    if (fr) {
        fr.querySelector('.cost-final-total').textContent = formatNumber(totalCost);
        fr.querySelector('.quote-final-total').textContent = formatNumber(finalQ);
        fr.querySelector('.difference-cell').textContent = formatNumber(finalQ - totalCost);
    }

    // 6. 이익률
    const mr = document.querySelector('.markup-row');
    if (mr && finalQ > 0) {
        const margin = (((finalQ - totalCost) / finalQ) * 100).toFixed(1);
        mr.querySelector('.margin-cell').textContent = margin + ' %';
    }
}

// 일괄 상승률 적용
function recalculateAllByGlobalRate(rate) {
    document.querySelectorAll('.category-row').forEach(row => {
        const costP = parseNumber(row.querySelector('.cost-price').textContent);
        row.querySelector('.row-upper').textContent = rate;
        row.querySelector('.quote-price').textContent = formatNumber(Math.round(costP * (1 + rate / 100)));
    });
    calculateAllTotals();
}

// ============================================================================
// 저장 기능
// ============================================================================

async function saveChanges() {
    if (!priceCompareId) return;
    if (!confirm('변경사항을 저장하시겠습니까?')) return;

    const rows = document.querySelectorAll('tr.category-row');
    const resources = [];
    
    rows.forEach(row => {
        resources.push({
            "machine_id": row.dataset.machineId,
            "machine_name": row.dataset.machineName,
            "major": row.dataset.major, // 💡 category -> major로 수정
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
    
    const body = {
        "creator": document.getElementById('creatorName').textContent.trim(),
        "description": document.getElementById('notesContent').textContent.trim(),
        "machine_ids": priceCompareData.machine_ids,
        "price_compare_resources": resources
    };

    try {
        const res = await fetch(`/api/v1/quotation/price_compare/${priceCompareId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        
        if (res.ok) {
            alert('저장되었습니다.');
            location.href = '?mode=view';
        } else {
            const err = await res.json();
            alert('저장 실패:\n' + JSON.stringify(err.detail, null, 2));
        }
    } catch (e) {
        alert('통신 오류 발생');
    }
}

// ============================================================================
// UI 모드 설정
// ============================================================================

function initUIByMode() {
    const isEdit = (pageMode === 'edit');
    const footer = document.getElementById('actionFooter');
    const notes = document.getElementById('notesContent');
    
    document.getElementById('pageTitle').textContent = isEdit ? '내정가 견적가 비교 (수정)' : '내정가 견적가 비교 (조회)';
    
    notes.textContent = priceCompareData.description || '';
    
    if (isEdit) {
        notes.contentEditable = "true";
        notes.classList.add('editable-note');
        footer.innerHTML = `<button class="btn btn-secondary btn-lg" onclick="location.href='?mode=view'">취소</button>
                            <button class="btn btn-primary btn-lg" onclick="saveChanges()">저장하기</button>`;
    } else {
        notes.contentEditable = "false";
        footer.innerHTML = `<button class="btn btn-secondary btn-lg" onclick="window.history.back()">목록으로</button>
                            <button class="btn btn-primary btn-lg" onclick="location.href='?mode=edit'">수정하기</button>`;
    }
}

// ============================================================================
// 유틸리티 함수
// ============================================================================

function parseNumber(t) {
    return parseInt(t?.toString().replace(/[^0-9.-]/g, '')) || 0;
}

function formatNumber(n) {
    return (n || 0).toLocaleString('ko-KR');
}