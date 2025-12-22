/**
 * 견적서(을지) 상세 페이지 - API 데이터 동적 렌더링
 * API: GET /api/v1/quotation/detailed/{detailed_id}
 */

let detailedId = null;
let detailedData = null;

// ============================================================================
// 페이지 초기화
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // URL에서 detailed_id 추출
    const pathParts = window.location.pathname.split('/');
    detailedId = pathParts[pathParts.length - 1];
    
    if (detailedId) {
        loadDetailedData(detailedId);
    } else {
        alert('견적서 ID가 없습니다.');
        goBack();
    }
});

// ============================================================================
// API 데이터 로드
// ============================================================================

async function loadDetailedData(id) {
    const loading = document.getElementById('loading');
    const table = document.getElementById('detailedTable');
    
    try {
        const response = await fetch(`/api/v1/quotation/detailed/${id}`);
        
        if (!response.ok) {
            throw new Error('데이터 로드 실패');
        }
        
        detailedData = await response.json();
        
        // 테이블 렌더링
        renderDetailedTable(detailedData.detailed_resources);
        
        // 로딩 숨기고 테이블 표시
        if (loading) loading.style.display = 'none';
        if (table) table.style.display = 'table';
        
    } catch (error) {
        console.error('Error:', error);
        alert('데이터를 불러오는데 실패했습니다.');
        if (loading) loading.innerHTML = '<p style="color: red;">데이터 로드 실패</p>';
    }
}

// ============================================================================
// 테이블 렌더링
// ============================================================================

function renderDetailedTable(resources) {
    const tbody = document.querySelector('.cover-inner table tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    // 1. machine_name + major로 그룹화
    const groups = groupByMachineThenMajor(resources);
    
    let html = '';
    let rowNumber = 1; // No 번호
    
    // 2. 각 machine별로 순회
    Object.keys(groups).forEach(machineName => {
        const majorGroups = groups[machineName];
        
        // 3. 각 major(항목)별로 순회
        Object.keys(majorGroups).forEach(major => {
            const items = majorGroups[major];
            
            // 섹션 타이틀 행
            const sectionTitle = getSectionTitle(major);
            html += `<tr class="section-title"><td colspan="8">${sectionTitle}</td></tr>`;
            
            // 데이터 행
            items.forEach(item => {
                html += `<tr>`;
                html += `<td>${rowNumber++}</td>`;
                html += `<td>${item.minor || ''}</td>`;
                html += `<td></td>`; // 규격 (비어있음)
                html += `<td>${item.compare || 1}</td>`;
                html += `<td>${item.unit || '식'}</td>`;
                html += `<td>${formatNumber(item.solo_price)}</td>`;
                html += `<td>${formatNumber(item.subtotal)}</td>`;
                html += `<td>${item.description || ''}</td>`;
                html += `</tr>`;
            });
            
            // 소계 행
            const subtotal = items.reduce((sum, item) => sum + item.subtotal, 0);
            html += renderSubtotalRow(major, subtotal);
        });
    });
    
    // 비고 영역
    html += `<tr class="notes-row">
                <td colspan="8" class="notes-header">비&nbsp;&nbsp;&nbsp;&nbsp;고&nbsp;(&nbsp;특이사항&nbsp;)</td>
             </tr>`;
    html += `<tr class="notes-row">
                <td colspan="8" class="notes-content">${detailedData.description || ''}</td>
             </tr>`;
    
    tbody.innerHTML = html;
    
    // 4. 전체 합계 계산
    calculateTotalPrice();
}

// machine → major로 그룹화
function groupByMachineThenMajor(resources) {
    const grouped = {};
    
    resources.forEach(item => {
        const machineName = item.machine_name || '미분류';
        const major = item.major || '기타';
        
        if (!grouped[machineName]) {
            grouped[machineName] = {};
        }
        if (!grouped[machineName][major]) {
            grouped[machineName][major] = [];
        }
        grouped[machineName][major].push(item);
    });
    
    return grouped;
}

// 섹션 타이틀 생성
function getSectionTitle(major) {
    const titles = {
        '자재비': '자재비 상세 내역',
        '인건비': '인건비 상세 내역',
        '출장 경비': '경비 상세 내역_국내',
        '출장경비': '경비 상세 내역_국내'
    };
    return titles[major] || `${major} 상세 내역`;
}

// 소계 행 렌더링
function renderSubtotalRow(major, subtotal) {
    let label = '';
    
    if (major === '자재비') {
        label = '자재비 총 합계';
    } else if (major === '인건비') {
        label = '인건비 총 합계';
    } else if (major.includes('출장') || major.includes('경비')) {
        label = '출장 경비 총 합계';
    } else {
        label = `${major} 총 합계`;
    }
    
    let html = `<tr class="summary-row">`;
    html += `<td colspan="2">${label}</td>`;
    html += `<td class="summary-white" colspan="4">Set</td>`;
    html += `<td class="summary-white total-amount">${formatNumber(subtotal)}</td>`;
    html += `<td class="summary-white"></td>`;
    html += `</tr>`;
    
    return html;
}

// 전체 합계 계산
function calculateTotalPrice() {
    const tfoot = document.querySelector('.cover-inner table tfoot');
    if (!tfoot) return;
    
    // 모든 소계 합산
    const summaryRows = document.querySelectorAll('.summary-row');
    let total = 0;
    
    summaryRows.forEach(row => {
        const amountCell = row.querySelector('.total-amount');
        if (amountCell) {
            const amount = parseNumber(amountCell.textContent);
            total += amount;
        }
    });
    
    // tfoot 업데이트
    tfoot.innerHTML = `
        <tr>
            <td colspan="7">Total</td>
            <td class="total-amount">${formatNumber(total)}</td>
        </tr>
    `;
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

function goBack() {
    window.history.back();
}