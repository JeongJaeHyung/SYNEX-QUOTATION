// ============================================================================
// 내정가 견적가 비교 페이지 - price_compare_detail.js
// API 데이터 기반 동적 렌더링
// ============================================================================

let priceCompareId = null;
let priceCompareData = null;
let markupRate = 5; // 기본 상승률 5%

// ============================================================================
// 페이지 초기화
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // URL에서 price_compare_id 추출
    const pathParts = window.location.pathname.split('/');
    priceCompareId = pathParts[pathParts.length - 1];
    
    if (priceCompareId) {
        loadPriceCompareData(priceCompareId);
    } else {
        alert('비교서 ID가 없습니다.');
        goBack();
    }
    
    // 상승률 입력 이벤트
    const markupInput = document.getElementById('markup-rate');
    if (markupInput) {
        markupInput.addEventListener('input', function() {
            markupRate = parseFloat(this.value) || 0;
            recalculateEstimates();
        });
    }
});

// ============================================================================
// API 데이터 로드
// ============================================================================

async function loadPriceCompareData(id) {
    const loading = document.getElementById('loading');
    const tableContainer = document.getElementById('tableContainer');
    const controlsContainer = document.getElementById('controlsContainer');
    const notesSection = document.getElementById('notesSection');
    const actionFooter = document.getElementById('actionFooter');
    
    loading.style.display = 'block';
    tableContainer.style.display = 'none';
    
    try {
        const response = await fetch(`/api/v1/quotation/price_compare/${id}`);
        
        if (!response.ok) {
            throw new Error('데이터 로드 실패');
        }
        
        priceCompareData = await response.json();
        
        // 작성자, 작성일 표시
        document.getElementById('creatorName').textContent = priceCompareData.creator || '-';
        document.getElementById('createdDate').textContent = formatDate(priceCompareData.created_at);
        
        // 테이블 렌더링
        renderComparisonTable(priceCompareData.price_compare_resources);
        
        // 특이사항 표시
        const notesContent = document.getElementById('notesContent');
        notesContent.textContent = priceCompareData.description || '내정가의 단가와 제출할 수 있는 견적가의 단가가 동일함. 내정가 단가는 실 금액 반영 필요';
        
        // UI 표시
        controlsContainer.style.display = 'flex';
        tableContainer.style.display = 'block';
        notesSection.style.display = 'block';
        actionFooter.style.display = 'flex';
        
    } catch (error) {
        console.error('Error:', error);
        alert('데이터를 불러오는데 실패했습니다.');
    } finally {
        loading.style.display = 'none';
    }
}

// ============================================================================
// 테이블 렌더링
// ============================================================================

function renderComparisonTable(resources) {
    const tbody = document.getElementById('comparisonTableBody');
    tbody.innerHTML = '';
    
    // 데이터를 major로 그룹화
    const groupedData = groupByMajor(resources);
    
    // 각 그룹별 렌더링
    let html = '';
    
    // 자재비
    if (groupedData['자재비'] && groupedData['자재비'].length > 0) {
        html += renderCategoryGroup('자재비', groupedData['자재비']);
    }
    
    // 인건비
    if (groupedData['인건비'] && groupedData['인건비'].length > 0) {
        html += renderCategoryGroup('인건비', groupedData['인건비']);
    }
    
    // 출장 경비 (있다면)
    if (groupedData['출장 경비'] && groupedData['출장 경비'].length > 0) {
        html += renderCategoryGroup('출장 경비', groupedData['출장 경비']);
    }
    
    // Sub Total
    html += renderSubTotalRow();
    
    // 관리비 (고정)
    html += renderManagementRows();
    
    // TOTAL
    html += renderFinalTotalRow();
    
    // 이익률
    html += renderMarkupRow();
    
    tbody.innerHTML = html;
    
    // 계산 실행
    calculateAllTotals();
}

// major로 그룹화
function groupByMajor(resources) {
    const groups = {};
    
    resources.forEach(item => {
        const major = item.major || '기타';
        if (!groups[major]) {
            groups[major] = [];
        }
        groups[major].push(item);
    });
    
    return groups;
}

// 카테고리 그룹 렌더링
function renderCategoryGroup(categoryName, items) {
    let html = '';
    const rowspan = items.length;
    
    items.forEach((item, index) => {
        html += '<tr class="category-row" data-category="' + categoryName + '">';
        
        // 첫 번째 행에만 카테고리 셀 추가
        if (index === 0) {
            html += `<td rowspan="${rowspan}" class="category-cell">${categoryName}</td>`;
        }
        
        // 구분
        html += `<td>${item.minor || ''}</td>`;
        
        // 내정가
        html += `<td class="cost-qty">${item.cost_compare || ''}</td>`;
        html += `<td>${item.cost_unit || ''}</td>`;
        html += `<td class="cost-price">${formatNumber(item.cost_solo_price)}</td>`;
        html += `<td class="cost-amount"></td>`;
        
        // 견적가
        html += `<td class="quote-qty">${item.quotation_compare || ''}</td>`;
        html += `<td>${item.quotation_unit || ''}</td>`;
        html += `<td class="quote-price" contenteditable="true" data-original="${item.quotation_solo_price}">${formatNumber(item.quotation_solo_price)}</td>`;
        html += `<td class="quote-amount"></td>`;
        
        // 비고
        html += `<td contenteditable="true">${item.description || ''}</td>`;
        
        html += '</tr>';
    });
    
    // 소계 행
    html += `<tr class="subtotal-row" data-subtotal-category="${categoryName}">`;
    html += `<td colspan="2">${categoryName} 소계</td>`;
    html += '<td></td><td></td><td></td>';
    html += '<td class="subtotal-cell cost-subtotal">0</td>';
    html += '<td></td><td></td><td></td>';
    html += '<td class="subtotal-cell quote-subtotal">0</td>';
    html += '<td class="difference-cell">0</td>';
    html += '</tr>';
    
    return html;
}

// Sub Total 행
function renderSubTotalRow() {
    let html = '<tr class="total-row">';
    html += '<td colspan="5">Sub Total</td>';
    html += '<td class="total-cell cost-total">0</td>';
    html += '<td></td><td></td><td></td>';
    html += '<td class="total-cell quote-total">0</td>';
    html += '<td class="difference-cell">0</td>';
    html += '</tr>';
    return html;
}

// 관리비 행
function renderManagementRows() {
    let html = '<tr class="management-row">';
    html += '<td rowspan="2" class="category-cell">관리비</td>';
    html += '<td>일반관리비</td>';
    html += '<td></td><td></td><td></td><td></td>';
    html += '<td class="mgmt-rate" contenteditable="true">6</td>';
    html += '<td></td><td></td>';
    html += '<td class="mgmt-amount">0</td>';
    html += '<td></td>';
    html += '</tr>';
    
    html += '<tr class="management-row">';
    html += '<td>기업이윤</td>';
    html += '<td></td><td></td><td></td><td></td>';
    html += '<td class="profit-rate" contenteditable="true">4</td>';
    html += '<td></td><td></td>';
    html += '<td class="profit-amount">0</td>';
    html += '<td></td>';
    html += '</tr>';
    
    return html;
}

// TOTAL 행
function renderFinalTotalRow() {
    let html = '<tr class="final-total-row">';
    html += '<td colspan="5">TOTAL</td>';
    html += '<td class="final-total-cell cost-final-total">0</td>';
    html += '<td></td><td></td><td></td>';
    html += '<td class="final-total-cell quote-final-total">0</td>';
    html += '<td class="difference-cell">0</td>';
    html += '</tr>';
    return html;
}

// 이익률 행
function renderMarkupRow() {
    let html = '<tr class="markup-row">';
    html += '<td colspan="9"></td>';
    html += '<td class="margin-cell">0 %</td>';
    html += '<td class="markup-cell">이익률</td>';
    html += '</tr>';
    return html;
}

// ============================================================================
// 계산 로직
// ============================================================================

function calculateAllTotals() {
    const tbody = document.getElementById('comparisonTableBody');
    const rows = tbody.querySelectorAll('tr');
    
    const categoryTotals = {}; // 카테고리별 합계
    let currentCategory = null;
    let costSum = 0;
    let quoteSum = 0;
    
    rows.forEach(row => {
        // 카테고리 행 처리
        if (row.classList.contains('category-row')) {
            const category = row.dataset.category;
            
            // 새 카테고리 시작
            if (category !== currentCategory) {
                // 이전 카테고리 저장
                if (currentCategory) {
                    categoryTotals[currentCategory] = { cost: costSum, quote: quoteSum };
                }
                
                currentCategory = category;
                costSum = 0;
                quoteSum = 0;
            }
            
            // 금액 계산
            const costQty = parseNumber(row.querySelector('.cost-qty')?.textContent);
            const costPrice = parseNumber(row.querySelector('.cost-price')?.textContent);
            const quoteQty = parseNumber(row.querySelector('.quote-qty')?.textContent);
            const quotePrice = parseNumber(row.querySelector('.quote-price')?.textContent);
            
            const costAmount = costQty * costPrice;
            const quoteAmount = quoteQty * quotePrice;
            
            // 금액 표시
            row.querySelector('.cost-amount').textContent = formatNumber(costAmount);
            row.querySelector('.quote-amount').textContent = formatNumber(quoteAmount);
            
            // 합계 누적
            costSum += costAmount;
            quoteSum += quoteAmount;
        }
        
        // 소계 행 처리
        if (row.classList.contains('subtotal-row')) {
            const category = row.dataset.subtotalCategory;
            
            // 마지막 카테고리 저장
            if (currentCategory) {
                categoryTotals[currentCategory] = { cost: costSum, quote: quoteSum };
            }
            
            // 소계 표시
            row.querySelector('.cost-subtotal').textContent = formatNumber(costSum);
            row.querySelector('.quote-subtotal').textContent = formatNumber(quoteSum);
            row.querySelector('.difference-cell').textContent = formatNumber(quoteSum - costSum);
            
            // 리셋
            currentCategory = null;
            costSum = 0;
            quoteSum = 0;
        }
    });
    
    // Sub Total 계산
    let totalCost = 0;
    let totalQuote = 0;
    
    Object.values(categoryTotals).forEach(totals => {
        totalCost += totals.cost;
        totalQuote += totals.quote;
    });
    
    const totalRow = tbody.querySelector('.total-row');
    if (totalRow) {
        totalRow.querySelector('.cost-total').textContent = formatNumber(totalCost);
        totalRow.querySelector('.quote-total').textContent = formatNumber(totalQuote);
        totalRow.querySelector('.difference-cell').textContent = formatNumber(totalQuote - totalCost);
    }
    
    // 관리비 계산
    const mgmtRow = tbody.querySelectorAll('.management-row')[0];
    const profitRow = tbody.querySelectorAll('.management-row')[1];
    
    const mgmtRate = parseFloat(mgmtRow.querySelector('.mgmt-rate').textContent) || 0;
    const profitRate = parseFloat(profitRow.querySelector('.profit-rate').textContent) || 0;
    
    const mgmtAmount = Math.round(totalQuote * mgmtRate / 100);
    const profitAmount = Math.round(totalQuote * profitRate / 100);
    
    mgmtRow.querySelector('.mgmt-amount').textContent = formatNumber(mgmtAmount);
    profitRow.querySelector('.profit-amount').textContent = formatNumber(profitAmount);
    
    // 최종 합계
    const finalQuoteTotal = totalQuote + mgmtAmount + profitAmount;
    
    const finalRow = tbody.querySelector('.final-total-row');
    if (finalRow) {
        finalRow.querySelector('.cost-final-total').textContent = formatNumber(totalCost);
        finalRow.querySelector('.quote-final-total').textContent = formatNumber(finalQuoteTotal);
        finalRow.querySelector('.difference-cell').textContent = formatNumber(finalQuoteTotal - totalCost);
    }
    
    // 이익률 계산
    const markupRow = tbody.querySelector('.markup-row');
    if (markupRow && finalQuoteTotal > 0) {
        const margin = ((finalQuoteTotal - totalCost) / finalQuoteTotal * 100).toFixed(0);
        markupRow.querySelector('.margin-cell').textContent = margin + ' %';
    }
}

// 견적가 재계산 (상승률 변경 시)
function recalculateEstimates() {
    const tbody = document.getElementById('comparisonTableBody');
    const rows = tbody.querySelectorAll('tr.category-row');
    
    rows.forEach(row => {
        const quotePriceCell = row.querySelector('.quote-price');
        if (quotePriceCell && !quotePriceCell.dataset.manual) {
            const originalPrice = parseFloat(quotePriceCell.dataset.original) || 0;
            const newPrice = Math.round(originalPrice * (1 + markupRate / 100));
            quotePriceCell.textContent = formatNumber(newPrice);
        }
    });
    
    calculateAllTotals();
}

// ============================================================================
// 이벤트 핸들러
// ============================================================================

// 견적 단가 수동 입력 처리
document.addEventListener('input', function(e) {
    if (e.target.classList.contains('quote-price')) {
        e.target.dataset.manual = 'true';
        calculateAllTotals();
    }
    
    if (e.target.classList.contains('mgmt-rate') || e.target.classList.contains('profit-rate')) {
        calculateAllTotals();
    }
});

// ============================================================================
// 저장 기능
// ============================================================================

async function saveChanges() {
    if (!priceCompareId) return;
    
    const tbody = document.getElementById('comparisonTableBody');
    const rows = tbody.querySelectorAll('tr.category-row');
    
    const updatedResources = [];
    
    rows.forEach(row => {
        const minor = row.cells[1]?.textContent.trim();
        const costQty = parseNumber(row.querySelector('.cost-qty')?.textContent);
        const costPrice = parseNumber(row.querySelector('.cost-price')?.textContent);
        const quoteQty = parseNumber(row.querySelector('.quote-qty')?.textContent);
        const quotePrice = parseNumber(row.querySelector('.quote-price')?.textContent);
        const description = row.cells[row.cells.length - 1]?.textContent.trim();
        
        const category = row.dataset.category;
        const costUnit = row.cells[3]?.textContent.trim();
        const quoteUnit = row.cells[7]?.textContent.trim();
        
        updatedResources.push({
            major: category,
            minor: minor,
            cost_solo_price: costPrice,
            cost_unit: costUnit,
            cost_compare: costQty,
            quotation_solo_price: quotePrice,
            quotation_unit: quoteUnit,
            quotation_compare: quoteQty,
            upper: markupRate,
            description: description
        });
    });
    
    const notesContent = document.getElementById('notesContent').textContent.trim();
    
    const requestData = {
        creator: priceCompareData.creator,
        description: notesContent,
        machine_ids: priceCompareData.machine_ids,
        price_compare_resources: updatedResources
    };
    
    try {
        const response = await fetch(`/api/v1/quotation/price_compare/${priceCompareId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        
        if (response.ok) {
            alert('저장되었습니다.');
            location.reload();
        } else {
            const error = await response.json();
            alert('저장 실패: ' + (error.detail || JSON.stringify(error)));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('저장 중 오류가 발생했습니다.');
    }
}

// ============================================================================
// 유틸리티 함수
// ============================================================================

function parseNumber(text) {
    if (!text || text.trim() === '' || text === '-') return 0;
    return parseInt(text.toString().replace(/,/g, '')) || 0;
}

function formatNumber(num) {
    if (num === 0 || num === null || num === undefined) return '';
    return num.toLocaleString('ko-KR');
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function goBack() {
    window.history.back();
}