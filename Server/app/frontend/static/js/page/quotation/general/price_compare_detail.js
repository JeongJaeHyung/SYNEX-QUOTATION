document.addEventListener('DOMContentLoaded', () => {
    loadPriceCompareData();
});

async function loadPriceCompareData() {
    // PRICE_COMPARE_ID는 HTML에서 전역 변수로 선언됨
    if(!PRICE_COMPARE_ID) return alert('ID가 없습니다.');

    try {
        //
        const res = await fetch(`/api/v1/quotation/price_compare/${PRICE_COMPARE_ID}?include_schema=true`);
        if(!res.ok) throw new Error('데이터 로드 실패');

        const data = await res.json();
        renderHeader(data);
        
        // 데이터가 없으면 빈 배열 처리
        const items = data.price_compare_resources || data.resources?.items || [];
        renderTableRows(items);

    } catch(e) {
        console.error(e);
        alert('데이터를 불러오는 중 오류가 발생했습니다.');
    }
}

function renderHeader(data) {
    if(data.description) document.getElementById('mainDescription').textContent = data.description;
    if(data.creator) document.getElementById('docCreator').textContent = `작성자: ${data.creator}`;
    if(data.created_at) document.getElementById('docDate').textContent = `작성일: ${new Date(data.created_at).toLocaleDateString()}`;
}

function renderTableRows(items) {
    // 1. 카테고리별 분류
    const groups = {
        material: items.filter(i => (i.major || i.category_major) === '자재비'),
        labor: items.filter(i => (i.major || i.category_major) === '인건비'),
        expense: items.filter(i => (i.major || i.category_major).includes('경비'))
    };

    // 2. 각 섹션 렌더링 및 합계 계산
    const matTotal = renderSection('materialBody', '자재비', groups.material);
    const labTotal = renderSection('laborBody', '인건비', groups.labor);
    const expTotal = renderSection('expenseBody', '경비', groups.expense);

    // 3. Sub Total 업데이트
    const subCost = matTotal.cost + labTotal.cost;
    const subQuot = matTotal.quot + labTotal.quot;

    document.getElementById('matCostTotal').textContent = formatNum(matTotal.cost);
    document.getElementById('matQuotTotal').textContent = formatNum(matTotal.quot);
    
    document.getElementById('labCostTotal').textContent = formatNum(labTotal.cost);
    document.getElementById('labQuotTotal').textContent = formatNum(labTotal.quot);
    
    document.getElementById('expCostTotal').textContent = formatNum(expTotal.cost);
    document.getElementById('expQuotTotal').textContent = formatNum(expTotal.quot);

    document.getElementById('subCostTotal').textContent = formatNum(subCost);
    document.getElementById('subQuotTotal').textContent = formatNum(subQuot);

    // 4. 관리비/이윤 계산 (견적가 기준 6%, 4% 가정)
    // 실제로는 DB에 저장된 값을 써야 할 수도 있으나, 여기선 자동계산 예시
    const adminRate = 0.06;
    const profitRate = 0.04;

    const adminFee = Math.round(subQuot * adminRate);
    const corpProfit = Math.round(subQuot * profitRate);

    document.getElementById('adminFee').textContent = formatNum(adminFee);
    document.getElementById('corpProfit').textContent = formatNum(corpProfit);

    // 5. Final Total
    // 내정가는 관리비/이윤 제외하고 Sub Total 그대로 (스크린샷 기준)
    const finalCost = subCost; 
    const finalQuot = subQuot + adminFee + corpProfit;

    document.getElementById('finalCostTotal').textContent = formatNum(finalCost);
    document.getElementById('finalQuotTotal').textContent = formatNum(finalQuot);

    // 이익률 계산 ( (견적 - 내정) / 견적 * 100 )
    if(finalQuot > 0) {
        const margin = ((finalQuot - finalCost) / finalQuot) * 100;
        document.getElementById('profitRate').textContent = `${margin.toFixed(1)}% 이익율`;
    }
}

/**
 * 섹션 렌더링 헬퍼 함수
 * @returns { cost: number, quot: number } 합계 객체
 */
function renderSection(tbodyId, label, items) {
    const tbody = document.getElementById(tbodyId);
    tbody.innerHTML = '';
    
    let totalCost = 0;
    let totalQuot = 0;

    items.forEach((item, index) => {
        const tr = document.createElement('tr');
        
        // 내정가 계산
        const costPrice = item.cost_solo_price || 0;
        const costQty = item.cost_compare || 0;
        const costAmt = costPrice * costQty;
        totalCost += costAmt;

        // 견적가 계산
        const quotPrice = item.quotation_solo_price || 0;
        const quotQty = item.quotation_compare || item.cost_compare || 0; // 견적 수량 없으면 내정 수량 사용
        const quotAmt = quotPrice * quotQty;
        totalQuot += quotAmt;

        // HTML 구성
        let html = '';
        
        // 첫 번째 행에만 대분류(rowspan) 표시
        if (index === 0) {
            html += `<td rowspan="${items.length}" class="text-center font-bold bg-white" style="vertical-align: top;">${label}</td>`;
        }

        html += `
            <td class="text-left">${item.minor || item.category_minor || item.model_name || '-'}</td>
            
            <td class="text-center yellow-bg">${formatNum(costQty)}</td>
            <td class="text-center yellow-bg">${item.cost_unit || item.unit || '식'}</td>
            <td class="text-right yellow-bg">${formatNum(costPrice)}</td>
            <td class="text-right yellow-bg">${formatNum(costAmt)}</td>
            
            <td class="text-center">${formatNum(quotQty)}</td>
            <td class="text-center">${item.quotation_unit || item.unit || '식'}</td>
            <td class="text-right">${formatNum(quotPrice)}</td>
            <td class="text-right">${formatNum(quotAmt)}</td>
            
            <td class="text-left" style="font-size: 11px;">${item.description || ''}</td>
        `;

        tr.innerHTML = html;
        tbody.appendChild(tr);
    });

    return { cost: totalCost, quot: totalQuot };
}

function formatNum(n) {
    return (n || 0).toLocaleString('ko-KR');
}