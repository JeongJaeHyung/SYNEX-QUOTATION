/**
 * 내정가 견적가 비교 상세 페이지 로직 - 최종 통합본
 * (행별 개별 상승률 관리 및 422 에러 완벽 해결)
 */

let priceCompareId = null;
let priceCompareData = null; // 서버 원본 데이터 보관용 (machine_ids 등 필수 필드 유지)
let pageMode = 'view'; // 기본값: 조회 모드

document.addEventListener('DOMContentLoaded', function() {
    // 1. URL 파라미터 및 경로에서 정보 추출
    const urlParams = new URLSearchParams(window.location.search);
    pageMode = urlParams.get('mode') || 'view';
    
    const pathParts = window.location.pathname.split('/');
    priceCompareId = pathParts[pathParts.length - 1];
    
    if (priceCompareId) {
        loadPriceCompareData(priceCompareId);
    }

    // 2. 상단 일괄 상승률 입력 이벤트
    const globalMarkupInput = document.getElementById('markup-rate');
    if (globalMarkupInput) {
        globalMarkupInput.addEventListener('input', function() {
            const rate = parseFloat(this.value) || 0;
            recalculateAllByGlobalRate(rate);
        });
    }

    // 3. 테이블 내 입력 시 실시간 계산 및 씽크 (이벤트 위임)
    const tbody = document.getElementById('comparisonTableBody');
    if (tbody) {
        tbody.addEventListener('input', function(e) {
            if (!e.target.hasAttribute('contenteditable')) return;

            const row = e.target.closest('tr');
            if (row.classList.contains('category-row')) {
                // 행별 개별 상승률(row-upper)을 수정했을 때
                if (e.target.classList.contains('row-upper')) {
                    const costPrice = parseNumber(row.querySelector('.cost-price').textContent);
                    const rowRate = parseFloat(e.target.textContent) || 0;
                    const newQuotePrice = Math.round(costPrice * (1 + rowRate / 100));
                    row.querySelector('.quote-price').textContent = formatNumber(newQuotePrice);
                } 
                // 견적 단가(quote-price)를 직접 수정했을 때 (상승률 역산)
                else if (e.target.classList.contains('quote-price')) {
                    const costPrice = parseNumber(row.querySelector('.cost-price').textContent);
                    const quotePrice = parseNumber(e.target.textContent);
                    if (costPrice > 0) {
                        const newUpper = ((quotePrice - costPrice) / costPrice * 100).toFixed(1);
                        row.querySelector('.row-upper').textContent = newUpper;
                    }
                }
            }
            // 최종 합계 및 이익률 재계산
            calculateAllTotals();
        });
    }
});

/**
 * 데이터 로드
 */
async function loadPriceCompareData(id) {
    const loading = document.getElementById('loading');
    try {
        loading.style.display = 'block';
        const response = await fetch(`/api/v1/quotation/price_compare/${id}`);
        if (!response.ok) throw new Error('데이터 로드 실패');
        
        priceCompareData = await response.json(); //
        
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

/**
 * 테이블 렌더링 (상승률 컬럼 추가)
 */
function renderComparisonTable(resources) {
    const tbody = document.getElementById('comparisonTableBody');
    const isEdit = (pageMode === 'edit');
    tbody.innerHTML = '';

    const groups = groupByMajor(resources);
    let html = '';

    Object.keys(groups).forEach(major => {
        const items = groups[major];
        items.forEach((item, idx) => {
            // machine_id 바인딩
            html += `<tr class="category-row" data-category="${major}" data-machine-id="${item.machine_id}">`;
            if (idx === 0) html += `<td rowspan="${items.length}" class="category-cell"><strong>${major}</strong></td>`;
            
            html += `<td class="minor-name">${item.minor || ''}</td>`;
            html += `<td class="cost-qty">${item.cost_compare || 0}</td>`;
            html += `<td>${item.cost_unit || '식'}</td>`;
            html += `<td class="cost-price">${formatNumber(item.cost_solo_price)}</td>`;
            html += `<td class="cost-amount">0</td>`;

            html += `<td class="quote-qty ${isEdit ? 'editable-cell' : ''}" ${isEdit ? 'contenteditable="true"' : ''}>${item.quotation_compare || 0}</td>`;
            html += `<td>${item.quotation_unit || '식'}</td>`;
            html += `<td class="quote-price ${isEdit ? 'editable-cell' : ''}" ${isEdit ? 'contenteditable="true"' : ''}>${formatNumber(item.quotation_solo_price)}</td>`;
            
            // [요청사항] 행별 개별 상승률 입력칸
            html += `<td class="row-upper ${isEdit ? 'editable-cell' : ''}" ${isEdit ? 'contenteditable="true"' : ''}>${item.upper || 0}</td>`;
            
            html += `<td class="quote-amount">0</td>`;
            html += `<td class="row-note ${isEdit ? 'editable-cell' : ''}" ${isEdit ? 'contenteditable="true"' : ''}>${item.description || ''}</td>`;
            html += `</tr>`;
        });

        html += `<tr class="subtotal-row" data-subtotal-category="${major}">
                    <td colspan="2">${major} 소계</td>
                    <td colspan="3"></td><td class="subtotal-cell cost-subtotal">0</td>
                    <td colspan="4"></td><td class="subtotal-cell quote-subtotal">0</td> <td class="difference-cell">0</td>
                 </tr>`;
    });

    // 요약 행 (관리비 등)
    html += `<tr class="total-row"><td colspan="5">Sub Total</td><td class="total-cell cost-total">0</td><td colspan="4"></td><td class="total-cell quote-total">0</td><td class="difference-cell">0</td></tr>
             <tr class="management-row"><td rowspan="2" class="category-cell">관리비</td><td>일반관리비</td><td colspan="5"></td><td class="mgmt-rate" ${isEdit ? 'contenteditable="true"' : ''}>6</td><td colspan="2"></td><td class="mgmt-amount">0</td><td></td></tr>
             <tr class="management-row"><td>기업이윤</td><td colspan="5"></td><td class="profit-rate" ${isEdit ? 'contenteditable="true"' : ''}>4</td><td colspan="2"></td><td class="profit-amount">0</td><td></td></tr>
             <tr class="final-total-row"><td colspan="5">TOTAL</td><td class="final-total-cell cost-final-total">0</td><td colspan="4"></td><td class="final-total-cell quote-final-total">0</td><td class="difference-cell">0</td></tr>
             <tr class="markup-row"><td colspan="10"></td><td class="margin-cell">0 %</td><td class="markup-cell">이익률</td></tr>`;

    tbody.innerHTML = html;
    calculateAllTotals();
}

/**
 * 실시간 계산 엔진 (씽크 보완)
 */
function calculateAllTotals() {
    const rows = document.querySelectorAll('tr.category-row');
    let totalCost = 0, totalQuote = 0;
    const catTotals = {};

    rows.forEach(row => {
        const cat = row.dataset.category;
        if (!catTotals[cat]) catTotals[cat] = { c: 0, q: 0 };

        const cq = parseNumber(row.querySelector('.cost-qty')?.textContent);
        const cp = parseNumber(row.querySelector('.cost-price')?.textContent);
        const qq = parseNumber(row.querySelector('.quote-qty')?.textContent);
        const qp = parseNumber(row.querySelector('.quote-price')?.textContent);

        const camt = cq * cp;
        const qamt = qq * qp;

        row.querySelector('.cost-amount').textContent = formatNumber(camt);
        row.querySelector('.quote-amount').textContent = formatNumber(qamt);

        catTotals[cat].c += camt;
        catTotals[cat].q += qamt;
    });

    // 소계 업데이트
    document.querySelectorAll('.subtotal-row').forEach(row => {
        const cat = row.dataset.subtotalCategory;
        const totals = catTotals[cat] || { c: 0, q: 0 };
        row.querySelector('.cost-subtotal').textContent = formatNumber(totals.c);
        row.querySelector('.quote-subtotal').textContent = formatNumber(totals.q);
        row.querySelector('.difference-cell').textContent = formatNumber(totals.q - totals.c);
        totalCost += totals.c; totalQuote += totals.q;
    });

    // TOTAL 및 관리비 계산
    const tr = document.querySelector('.total-row');
    if (tr) {
        tr.querySelector('.cost-total').textContent = formatNumber(totalCost);
        tr.querySelector('.quote-total').textContent = formatNumber(totalQuote);
    }

    let mgmtSum = 0;
    document.querySelectorAll('.management-row').forEach(row => {
        const rate = parseFloat(row.querySelector('.mgmt-rate, .profit-rate')?.textContent) || 0;
        const amt = Math.round(totalQuote * (rate / 100));
        row.querySelector('.mgmt-amount, .profit-amount').textContent = formatNumber(amt);
        mgmtSum += amt;
    });

    const finalQ = totalQuote + mgmtSum;
    const fr = document.querySelector('.final-total-row');
    if (fr) {
        fr.querySelector('.cost-final-total').textContent = formatNumber(totalCost);
        fr.querySelector('.quote-final-total').textContent = formatNumber(finalQ);
        fr.querySelector('.difference-cell').textContent = formatNumber(finalQ - totalCost);
    }

    const mr = document.querySelector('.markup-row');
    if (mr && finalQ > 0) {
        mr.querySelector('.margin-cell').textContent = (((finalQ - totalCost) / finalQ) * 100).toFixed(1) + ' %';
    }
}

/**
 * 상단 일괄 상승률 적용
 */
function recalculateAllByGlobalRate(rate) {
    document.querySelectorAll('.category-row').forEach(row => {
        const costP = parseNumber(row.querySelector('.cost-price').textContent);
        row.querySelector('.row-upper').textContent = rate;
        row.querySelector('.quote-price').textContent = formatNumber(Math.round(costP * (1 + rate / 100)));
    });
    calculateAllTotals();
}

/**
 * 저장 (PUT) - 명세서 필수 필드 완벽 대응
 */
async function saveChanges() {
    if (!priceCompareId) return;
    if (!confirm('변경사항을 저장하시겠습니까?')) return;

    const rows = document.querySelectorAll('tr.category-row');
    const resources = [];
    
    rows.forEach(row => {
        resources.push({
            "machine_id": row.dataset.machineId,
            "major": row.dataset.category,
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
        "machine_ids": priceCompareData.machine_ids, //
        "price_compare_resources": resources
    };

    try {
        const res = await fetch(`/api/v1/quotation/price_compare/${priceCompareId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        if (res.ok) { alert('저장되었습니다.'); location.href = '?mode=view'; }
        else { const err = await res.json(); alert('저장 실패:\n' + JSON.stringify(err.detail, null, 2)); }
    } catch (e) { alert('통신 오류 발생'); }
}

/**
 * 유틸리티 함수
 */
function parseNumber(t) {
    return parseInt(t?.toString().replace(/[^0-9.-]/g, '')) || 0;
}
function formatNumber(n) {
    return (n || 0).toLocaleString('ko-KR');
}
function groupByMajor(r) {
    return r.reduce((a, o) => {
        const k = o.major || '기타';
        if (!a[k]) a[k] = [];
        a[k].push(o);
        return a;
    }, {});
}
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