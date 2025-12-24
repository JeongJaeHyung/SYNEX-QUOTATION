/**
 * 견적서 갑지 페이지 - Excel 생성 기능 포함
 * ExcelJS 4.3.0 및 FileSaver.js 2.0.5 필요
 */

let headerId = null;
let headerData = null;
let isEditMode = false;

// ============================================================================
// 페이지 초기화
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('[견적서 갑지] 페이지 로드 시작');
    
    const pathParts = window.location.pathname.split('/');
    headerId = pathParts[pathParts.length - 1];
    
    console.log('[견적서 갑지] Header ID:', headerId);
    
    if (headerId && headerId !== 'detail') {
        loadHeaderData(headerId);
    } else {
        console.error('[견적서 갑지] ID가 없습니다.');
        alert('견적서 ID가 없습니다.');
    }
    
    setupEventListeners();
});

// ============================================================================
// API 데이터 로드
// ============================================================================

async function loadHeaderData(id) {
    const loading = document.getElementById('loading');
    const container = document.getElementById('summaryContainer');
    const sideMenu = document.getElementById('sideActionMenu');
    
    console.log('[견적서 갑지] API 호출 시작:', `/api/v1/quotation/header/${id}`);
    
    try {
        const response = await fetch(`/api/v1/quotation/header/${id}`);
        
        if (!response.ok) {
            throw new Error('데이터 로드 실패');
        }
        
        headerData = await response.json();
        console.log('[견적서 갑지] API 응답:', headerData);
        
        renderHeaderData(headerData);
        
        if (loading) loading.style.display = 'none';
        if (container) container.style.display = 'block';
        if (sideMenu) sideMenu.style.display = 'flex';
        
    } catch (error) {
        console.error('[견적서 갑지] Error:', error);
        alert('데이터를 불러오는데 실패했습니다.');
        if (loading) loading.innerHTML = '<p style="color: red;">데이터 로드 실패</p>';
    }
}

// ============================================================================
// 데이터 렌더링
// ============================================================================

function renderHeaderData(data) {
    console.log('[견적서 갑지] 데이터 렌더링 시작');
    
    renderBasicInfo(data);
    renderTable(data.header_resources);
    updateCalculations();
    
    console.log('[견적서 갑지] 렌더링 완료');
}

function renderBasicInfo(data) {
    const today = new Date();
    document.getElementById('quotationDate').textContent = formatDate(today);
    
    if (data.client) {
        document.getElementById('senderCompany').textContent = data.client;
    }
    
    if (data.title) {
        document.getElementById('documentTitle').textContent = data.title;
        document.getElementById('quotationTitle').textContent = data.title;
    }
    
    if (data.pic_name && data.pic_position) {
        document.getElementById('picInfoLabel').textContent = 
            `${data.pic_name} ${data.pic_position}님 귀하`;
    }
    
    if (data.description_1) {
        document.getElementById('remarksSpecial').textContent = data.description_1;
    } else {
        document.getElementById('remarksSpecial').textContent = '1. 2개라인 기준의 견적서 입니다.';
    }
    
    if (data.description_2) {
        document.getElementById('remarksGeneral').textContent = data.description_2;
    } else {
        document.getElementById('remarksGeneral').innerHTML = 
            '- 납기 : 협의사항<br>- 지불조건 : 선급금 30%, 중도금 50%, 잔금 20%<br>- 기타 : 견적유효기간 10 일';
    }
}

function renderTable(resources) {
    const tbody = document.getElementById('quotationTableBody');
    if (!tbody) return;
    
    const existingRows = tbody.querySelectorAll('tr:not(.empty-row)');
    existingRows.forEach(row => row.remove());
    
    let html = '';
    
    resources.forEach((item, index) => {
        const rowNumber = index + 1;
        const quantity = item.compare || 1;
        const unit = item.unit || '식';
        const price = item.solo_price || 0;
        const subtotal = item.subtotal || (price * quantity);
        
        html += `<tr>`;
        html += `<td class="col-no col-center">${rowNumber}</td>`;
        html += `<td class="col-machine col-center">${item.machine || ''}</td>`;
        html += `<td class="col-name col-center">${item.name || ''}</td>`;
        html += `<td class="col-spec col-center" contenteditable="true">${item.spac || ''}</td>`;
        html += `<td class="col-quantity col-center" contenteditable="true">${quantity}</td>`;
        html += `<td class="col-unit col-center" contenteditable="true">${unit}</td>`;
        html += `<td class="col-price col-right" contenteditable="true">${formatNumber(price)}</td>`;
        html += `<td class="col-unit-price col-right">${formatNumber(subtotal)}</td>`;
        html += `<td class="col-remarks col-left" contenteditable="true">${item.description || ''}</td>`;
        html += `</tr>`;
    });
    
    tbody.innerHTML = html;
}

// ============================================================================
// 편집 모드
// ============================================================================

function toggleEditMode(mode) {
    const container = document.getElementById('summaryContainer');
    const btn = document.getElementById('btnToggleEdit');
    
    if (mode === 'edit') {
        if (isEditMode) {
            saveSummary();
        } else {
            isEditMode = true;
            container.classList.add('edit-mode');
            btn.textContent = '저장하기';
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-success');
            
            const editables = document.querySelectorAll('.editable-text');
            editables.forEach(el => el.setAttribute('contenteditable', 'true'));
        }
    } else if (mode === 'cancel') {
        isEditMode = false;
        container.classList.remove('edit-mode');
        btn.textContent = '수정하기';
        btn.classList.remove('btn-success');
        btn.classList.add('btn-primary');
        
        const editables = document.querySelectorAll('.editable-text');
        editables.forEach(el => el.setAttribute('contenteditable', 'false'));
        
        loadHeaderData(headerId);
    }
}

// ============================================================================
// 이벤트 리스너
// ============================================================================

function setupEventListeners() {
    const editableCells = document.querySelectorAll('[contenteditable="true"]');
    editableCells.forEach(cell => {
        cell.addEventListener('input', handleCellEdit);
        cell.addEventListener('blur', updateCalculations);
    });

    editableCells.forEach((cell, index) => {
        cell.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const nextCell = editableCells[index + 1];
                if (nextCell) {
                    nextCell.focus();
                }
            }
        });
    });

    const negoTotal = document.getElementById('negoTotal');
    if (negoTotal) {
        negoTotal.addEventListener('blur', (e) => {
            const val = parseInt(e.target.textContent.replace(/[^0-9]/g, '')) || 0;
            if (val > 0) {
                 e.target.textContent = formatNumber(val);
            }
            updateCalculations();
        });
    }
}

function handleCellEdit(e) {
    const cell = e.target;
    if (cell.classList.contains('col-right')) {
        const value = cell.textContent.replace(/[^0-9]/g, '');
        if (value) {
            cell.textContent = formatNumber(parseInt(value));
        }
    }
}

// ============================================================================
// 계산 함수
// ============================================================================

let isFirstCalculation = true;

function updateCalculations() {
    const tbody = document.getElementById('quotationTableBody');
    const rows = tbody.querySelectorAll('tr:not(.empty-row)');
    let total = 0;
    let totalQty = 0;

    rows.forEach((row) => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 8) {
            const priceText = cells[6].textContent.replace(/[^0-9]/g, '');
            const quantityText = cells[4].textContent.replace(/[^0-9.-]/g, '');

            const price = parseInt(priceText) || 0;
            const quantity = parseFloat(quantityText) || 0;
            const amount = price * quantity;

            cells[7].textContent = formatNumber(amount);
            total += amount;
            totalQty += quantity;
        }
    });

    document.getElementById('summaryAmount').textContent = formatNumber(total);
    document.getElementById('totalAmount').textContent = formatNumber(total);
    document.getElementById('totalQtySum').textContent = totalQty;
    
    const negoTotal = document.getElementById('negoTotal');
    if (isFirstCalculation && negoTotal) {
        negoTotal.textContent = formatNumber(total);
    }
    
    let finalAmount = total;
    if (negoTotal) {
        const negoVal = parseInt(negoTotal.textContent.replace(/[^0-9]/g, '')) || 0;
        if (negoVal > 0) {
            finalAmount = negoVal;
        }
    }

    const totalAmountVat = document.getElementById('totalAmountVat');
    const quotationAmountText = document.getElementById('quotationAmountText');
    
    if (totalAmountVat) {
        totalAmountVat.textContent = formatNumber(finalAmount);
    }
    
    if (quotationAmountText) {
        quotationAmountText.textContent = numberToKorean(finalAmount);
    }

    isFirstCalculation = false;
}

// ============================================================================
// 데이터 저장
// ============================================================================

async function saveSummary() {
    if (!headerId || !headerData) {
        alert('데이터가 없습니다.');
        return;
    }
    
    try {
        const summaryData = collectSummaryData();
        console.log('[견적서 갑지] 저장할 데이터:', summaryData);

        const response = await fetch(`/api/v1/quotation/header/${headerId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(summaryData)
        });

        if (response.ok) {
            alert('저장되었습니다.');
            await loadHeaderData(headerId);
            toggleEditMode('cancel');
        } else {
            throw new Error('저장 실패');
        }

    } catch (error) {
        console.error('[견적서 갑지] 저장 오류:', error);
        alert('저장 중 오류가 발생했습니다.');
    }
}

function collectSummaryData() {
    return {
        title: document.getElementById('documentTitle').textContent,
        client: document.getElementById('senderCompany').textContent,
        description_1: document.getElementById('remarksSpecial').textContent,
        description_2: document.getElementById('remarksGeneral').textContent || document.getElementById('remarksGeneral').innerHTML.replace(/<br>/g, '\n'),
        header_resources: collectTableData()
    };
}

function collectTableData() {
    const tbody = document.getElementById('quotationTableBody');
    const rows = tbody.querySelectorAll('tr:not(.empty-row)');
    const items = [];

    rows.forEach((row, index) => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 9) {
            const originalResource = headerData.header_resources[index];
            
            items.push({
                machine: originalResource?.machine || '',
                name: cells[2].textContent.trim(),
                spac: cells[3].textContent.trim(),
                compare: parseInt(cells[4].textContent.replace(/[^0-9]/g, '')) || 1,
                unit: cells[5].textContent.trim(),
                solo_price: parseInt(cells[6].textContent.replace(/[^0-9]/g, '')) || 0,
                description: cells[8].textContent.trim()
            });
        }
    });

    return items;
}

// ============================================================================
// Excel 생성 함수 (갑지_예시.xlsx 완전 동일 + 동적 확장)
// ============================================================================

async function exportHeaderToExcel() {
    console.log('[Excel] 생성 시작');
    
    if (!headerData) {
        alert('데이터가 없습니다.');
        return;
    }

    try {
        const ExcelJS = window.ExcelJS;
        const workbook = new ExcelJS.Workbook();
        const worksheet = workbook.addWorksheet('Sheet1');

        // 컬럼 너비 설정
        worksheet.columns = [
            { width: 4.0 },      // A
            { width: 22.5 },     // B
            { width: 13.0 },     // C
            { width: 6.0 },      // D
            { width: 5.5 },      // E
            { width: 13.0 },     // F
            { width: 13.375 },   // G
            { width: 12.375 },   // H
            { width: 9.0 },      // I
            { width: 19.5 },     // J
            { width: 5.625 }     // K
        ];

        // ===== Row 1: 공백 =====
        worksheet.getRow(1).height = 15;

        // ===== Row 2: QUOTATION 타이틀 =====
        worksheet.mergeCells('A2:K2');
        const titleCell = worksheet.getCell('A2');
        titleCell.value = 'QUOTATION';
        titleCell.font = { name: '맑은 고딕', size: 33, bold: true };
        titleCell.alignment = { horizontal: 'center', vertical: 'center' };
        titleCell.border = {
            top: { style: 'medium' },
            left: { style: 'medium' },
            right: { style: 'medium' }
        };
        
        // QUOTATION 셀 전체에 medium 테두리 적용
        for (let col = 1; col <= 11; col++) {
            const cell = worksheet.getCell(2, col);
            cell.border = {
                top: { style: 'medium' },
                left: col === 1 ? { style: 'medium' } : { style: 'thin' },
                right: col === 11 ? { style: 'medium' } : { style: 'thin' }
            };
        }
        
        worksheet.getRow(2).height = 42.75;

        // ===== Row 3: 날짜 및 공급자 정보 시작 =====
        worksheet.mergeCells('B3:D3');
        const dateCell = worksheet.getCell('B3');
        const today = new Date();
        dateCell.value = formatDate(today);
        dateCell.font = { name: '맑은 고딕', size: 11 };
        dateCell.alignment = { horizontal: 'left', vertical: 'center' };
        dateCell.border = {
            left: { style: 'medium' },
            right: { style: 'thin' }
        };

        worksheet.mergeCells('F3:F7');
        const supplierLabel = worksheet.getCell('F3');
        supplierLabel.value = '공 급 자';
        supplierLabel.font = { name: '맑은 고딕', size: 11, bold: true };
        supplierLabel.alignment = { horizontal: 'center', vertical: 'center' };
        supplierLabel.border = {
            top: { style: 'medium' },
            left: { style: 'medium' },
            bottom: { style: 'medium' }
        };

        worksheet.getCell('G3').value = '견적 번호';
        worksheet.getCell('G3').alignment = { horizontal: 'center', vertical: 'center' };
        worksheet.getCell('G3').font = { name: '맑은 고딕', size: 9 };
        worksheet.getCell('G3').border = { 
            top: { style: 'medium' },
            left: { style: 'thin' },
            right: { style: 'thin' }
        };

        worksheet.mergeCells('H3:J3');
        worksheet.getCell('H3').value = '00-251126-01-01-01';
        worksheet.getCell('H3').alignment = { horizontal: 'center', vertical: 'center' };
        worksheet.getCell('H3').font = { name: '맑은 고딕', size: 9 };
        worksheet.getCell('H3').border = { 
            top: { style: 'medium' }
        };
        worksheet.getCell('K3').border = {
            top: { style: 'medium' },
            right: { style: 'medium' }
        };

        // ===== Row 4: 고객사명 및 공급자 상호 =====
        worksheet.mergeCells('B4:D5');
        const clientCell = worksheet.getCell('B4');
        clientCell.value = headerData.client || '㈜엠플러스';
        clientCell.font = { name: '맑은 고딕', size: 15, bold: true };
        clientCell.alignment = { horizontal: 'left', vertical: 'center' };
        clientCell.border = {
            left: { style: 'medium' },
            right: { style: 'thin' }
        };

        worksheet.getCell('G4').value = '상호(법인명)';
        worksheet.getCell('G4').alignment = { horizontal: 'center', vertical: 'center' };
        worksheet.getCell('G4').font = { name: '맑은 고딕', size: 9 };
        worksheet.getCell('G4').border = {
            left: { style: 'thin' },
            right: { style: 'thin' }
        };

        worksheet.mergeCells('H4:I4');
        worksheet.getCell('H4').value = '(주)시넥스플러스';
        worksheet.getCell('H4').alignment = { horizontal: 'center', vertical: 'center' };
        worksheet.getCell('H4').font = { name: '맑은 고딕', size: 9 };

        worksheet.getCell('J4').value = '성  명';
        worksheet.getCell('J4').alignment = { horizontal: 'center', vertical: 'center' };
        worksheet.getCell('J4').font = { name: '맑은 고딕', size: 9 };
        worksheet.getCell('K4').border = {
            right: { style: 'medium' }
        };

        // ===== Row 5: 사업장주소 =====
        worksheet.mergeCells('H5:J5');
        worksheet.getCell('G5').value = '사업장주소';
        worksheet.getCell('G5').alignment = { horizontal: 'center', vertical: 'center' };
        worksheet.getCell('G5').font = { name: '맑은 고딕', size: 9 };
        worksheet.getCell('G5').border = {
            left: { style: 'thin' },
            right: { style: 'thin' }
        };
        
        worksheet.getCell('H5').value = '인천광역시 연수구 송도과학로';
        worksheet.getCell('H5').alignment = { horizontal: 'center', vertical: 'center' };
        worksheet.getCell('H5').font = { name: '맑은 고딕', size: 9 };
        
        worksheet.getCell('K5').border = {
            right: { style: 'medium' }
        };

        // ===== Row 6: 담당자 및 업태 =====
        worksheet.mergeCells('B6:D6');
        const picCell = worksheet.getCell('B6');
        picCell.value = `${headerData.pic_name || '이중남'} ${headerData.pic_position || '차장'}님 귀하`;
        picCell.font = { name: '맑은 고딕', size: 11 };
        picCell.alignment = { horizontal: 'left', vertical: 'center' };
        picCell.border = {
            left: { style: 'medium' },
            right: { style: 'thin' }
        };

        worksheet.getCell('G6').value = '업    태';
        worksheet.getCell('G6').alignment = { horizontal: 'center', vertical: 'center' };
        worksheet.getCell('G6').font = { name: '맑은 고딕', size: 9 };
        worksheet.getCell('G6').border = {
            left: { style: 'thin' },
            right: { style: 'thin' }
        };

        worksheet.mergeCells('H6:I6');
        worksheet.getCell('H6').value = '서비스';
        worksheet.getCell('H6').alignment = { horizontal: 'center', vertical: 'center' };
        worksheet.getCell('H6').font = { name: '맑은 고딕', size: 9 };

        worksheet.getCell('J6').value = '사업자번호';
        worksheet.getCell('J6').alignment = { horizontal: 'center', vertical: 'center' };
        worksheet.getCell('J6').font = { name: '맑은 고딕', size: 9 };
        
        worksheet.getCell('K6').border = {
            right: { style: 'medium' }
        };

        // ===== Row 7: 인사말 및 연락처 =====
        worksheet.mergeCells('B7:D7');
        worksheet.getCell('B7').value = '아래와 같이 견적합니다.';
        worksheet.getCell('B7').font = { name: '맑은 고딕', size: 11 };
        worksheet.getCell('B7').alignment = { horizontal: 'left', vertical: 'center' };
        worksheet.getCell('B7').border = {
            left: { style: 'medium' },
            right: { style: 'thin' }
        };

        worksheet.getCell('G7').value = 'TEL';
        worksheet.getCell('G7').alignment = { horizontal: 'center', vertical: 'center' };
        worksheet.getCell('G7').font = { name: '맑은 고딕', size: 9 };
        worksheet.getCell('G7').border = { 
            bottom: { style: 'medium' },
            left: { style: 'thin' },
            right: { style: 'thin' }
        };

        worksheet.mergeCells('H7:I7');
        worksheet.getCell('H7').value = '010-1234-5678';
        worksheet.getCell('H7').alignment = { horizontal: 'center', vertical: 'center' };
        worksheet.getCell('H7').font = { name: '맑은 고딕', size: 9 };
        worksheet.getCell('H7').border = { bottom: { style: 'medium' } };

        worksheet.getCell('J7').value = 'mail';
        worksheet.getCell('J7').alignment = { horizontal: 'center', vertical: 'center' };
        worksheet.getCell('J7').font = { name: '맑은 고딕', size: 9 };
        worksheet.getCell('J7').border = { bottom: { style: 'medium' } };
        
        worksheet.getCell('K7').border = { 
            bottom: { style: 'medium' },
            right: { style: 'medium' }
        };

        // ===== Row 8-9: 제목 및 견적금액 =====
        worksheet.mergeCells('A8:A9');
        worksheet.mergeCells('B8:D9');
        const titleTextCell = worksheet.getCell('B8');
        titleTextCell.value = `제목 : ${headerData.title || 'HMC 차세대 배터리 라인'}`;
        titleTextCell.font = { name: '맑은 고딕', size: 12, bold: true };
        titleTextCell.alignment = { horizontal: 'left', vertical: 'center', wrapText: true };

        // ✅ 수정: 견적금액은 H8에만
        const totalPrice = headerData.price || 0;
        worksheet.getCell('H8').value = '견적금액 :';
        worksheet.getCell('H8').font = { name: '맑은 고딕', size: 11, bold: true };
        worksheet.getCell('H8').alignment = { horizontal: 'center', vertical: 'center' };

        // ✅ 수정: 한글 금액 표시는 I8:J8 병합
        worksheet.mergeCells('I8:J8');
        worksheet.getCell('I8').value = numberToKorean(totalPrice);
        worksheet.getCell('I8').font = { name: '맑은 고딕', size: 11, bold: true };
        worksheet.getCell('I8').alignment = { horizontal: 'left', vertical: 'center' };

        // Row 9: ₩ 금액 (VAT별도)
        worksheet.mergeCells('I9:J9');
        worksheet.getCell('I9').value = `₩${formatNumber(totalPrice)} (VAT별도)`;
        worksheet.getCell('I9').font = { name: '맑은 고딕', size: 11, bold: true };
        worksheet.getCell('I9').alignment = { horizontal: 'right', vertical: 'center' };

        // ===== Row 10: 문서 타이틀 =====
        worksheet.mergeCells('A10:K10');
        const docTitleCell = worksheet.getCell('A10');
        docTitleCell.value = headerData.title || 'HMC 차세대 배터리 라인 주액기_전장_견적서';
        docTitleCell.font = { name: '맑은 고딕', size: 11, bold: true };
        docTitleCell.alignment = { horizontal: 'center', vertical: 'center' };
        docTitleCell.fill = {
            type: 'pattern',
            pattern: 'solid',
            fgColor: { argb: 'FFD9EAF7' }
        };
        docTitleCell.border = {
            top: { style: 'medium' },
            bottom: { style: 'medium' },
            left: { style: 'medium' },
            right: { style: 'medium' }
        };
        worksheet.getRow(10).height = 17.25;

        // ===== Row 11: 테이블 헤더 =====
        const headers = ['No', '장비명', '품     명', '규 격', '수량', '단위', '단 가', '공급가액', '', '비 고', ''];
        const headerRow = worksheet.getRow(11);
        
        // ✅ 수정: 공급가액(H:I), 비고(J:K) 병합
        worksheet.mergeCells('H11:I11');
        worksheet.mergeCells('J11:K11');
        
        headers.forEach((header, idx) => {
            if (idx === 8 || idx === 10) return; // 병합된 셀 건너뛰기
            
            const cell = headerRow.getCell(idx + 1);
            cell.value = header;
            cell.font = { name: '맑은 고딕', size: 10, bold: true };
            cell.alignment = { horizontal: 'center', vertical: 'center' };
            cell.fill = {
                type: 'pattern',
                pattern: 'solid',
                fgColor: { argb: 'FFFFFFE0' }
            };
            cell.border = {
                top: { style: 'thin' },
                bottom: { style: 'thin' },
                left: { style: 'thin' },
                right: { style: 'thin' }
            };
        });

        // ===== 동적 데이터 행 =====
        let currentRow = 12;
        const dataRowCount = headerData.header_resources.length;
        
        headerData.header_resources.forEach((item, index) => {
            const row = worksheet.getRow(currentRow);
            
            row.getCell(1).value = index + 1;        // No
            row.getCell(2).value = item.machine || '';  // 장비명
            row.getCell(3).value = item.name || '';     // 품명
            row.getCell(4).value = item.spac || '';     // 규격
            row.getCell(5).value = item.compare || 1;   // 수량
            row.getCell(6).value = item.unit || '원';   // 단위
            row.getCell(7).value = item.solo_price || 0;  // 단가
            
            // ✅ 수정: 공급가액 H:I 병합
            worksheet.mergeCells(`H${currentRow}:I${currentRow}`);
            row.getCell(8).value = item.subtotal || 0;  // 공급가액
            
            // ✅ 수정: 비고 J:K 병합
            worksheet.mergeCells(`J${currentRow}:K${currentRow}`);
            row.getCell(10).value = item.description || '';  // 비고

            // 스타일 적용
            for (let col = 1; col <= 11; col++) {
                const cell = row.getCell(col);
                cell.font = { name: '맑은 고딕', size: 10 };
                cell.border = {
                    top: { style: 'thin' },
                    bottom: { style: 'thin' },
                    left: { style: 'thin' },
                    right: { style: 'thin' }
                };
                
                // 정렬
                if (col <= 6) {
                    cell.alignment = { horizontal: 'center', vertical: 'center' };
                } else if (col === 7) {
                    cell.alignment = { horizontal: 'right', vertical: 'center' };
                    cell.numFmt = '#,##0';
                } else if (col === 8 || col === 9) {
                    cell.alignment = { horizontal: 'right', vertical: 'center' };
                    if (col === 8) cell.numFmt = '#,##0';
                } else {
                    cell.alignment = { horizontal: 'left', vertical: 'center' };
                }
            }
            
            currentRow++;
        });

        // ✅ 동적: 견적 총 합계 행 (데이터 바로 다음)
        const summaryRow = currentRow;
        worksheet.mergeCells(`A${summaryRow}:D${summaryRow}`);
        worksheet.getCell(`A${summaryRow}`).value = '견적 총 합계';
        worksheet.getCell(`A${summaryRow}`).font = { name: '맑은 고딕', size: 11, bold: true };
        worksheet.getCell(`A${summaryRow}`).alignment = { horizontal: 'center', vertical: 'center' };
        worksheet.getCell(`A${summaryRow}`).fill = {
            type: 'pattern',
            pattern: 'solid',
            fgColor: { argb: 'FFD9EAF7' }
        };

        const totalQtySum = headerData.header_resources.reduce((sum, item) => sum + (item.compare || 1), 0);
        worksheet.getCell(`E${summaryRow}`).value = totalQtySum;
        worksheet.getCell(`E${summaryRow}`).alignment = { horizontal: 'center', vertical: 'center' };
        
        worksheet.getCell(`F${summaryRow}`).value = 'Set';
        worksheet.getCell(`F${summaryRow}`).alignment = { horizontal: 'center', vertical: 'center' };

        // ✅ 수정: 공급가액 H:I 병합
        worksheet.mergeCells(`H${summaryRow}:I${summaryRow}`);
        const totalAmount = headerData.price || 0;
        worksheet.getCell(`H${summaryRow}`).value = totalAmount;
        worksheet.getCell(`H${summaryRow}`).numFmt = '#,##0';
        worksheet.getCell(`H${summaryRow}`).alignment = { horizontal: 'right', vertical: 'center' };
        worksheet.getCell(`H${summaryRow}`).font = { name: '맑은 고딕', size: 11, bold: true };
        worksheet.getCell(`H${summaryRow}`).fill = {
            type: 'pattern',
            pattern: 'solid',
            fgColor: { argb: 'FFD9EAF7' }
        };

        worksheet.getRow(summaryRow).height = 17.25;

        // ===== 비고 (특이사항) - 동적 위치 =====
        currentRow = summaryRow + 1;
        
        worksheet.mergeCells(`A${currentRow}:K${currentRow}`);
        worksheet.getCell(`A${currentRow}`).value = '비    고 ( 특이사항 )';
        worksheet.getCell(`A${currentRow}`).font = { name: '맑은 고딕', size: 11, bold: true };
        worksheet.getCell(`A${currentRow}`).alignment = { horizontal: 'center', vertical: 'center' };
        worksheet.getCell(`A${currentRow}`).fill = {
            type: 'pattern',
            pattern: 'solid',
            fgColor: { argb: 'FFFFFFE0' }
        };

        currentRow++;
        worksheet.mergeCells(`A${currentRow}:K${currentRow}`);
        // ✅ 수정: 화면의 description_1 참조
        const specialRemarks = document.getElementById('remarksSpecial')?.textContent || headerData.description_1 || '1. 2개라인 기준의 견적서 입니다.';
        worksheet.getCell(`A${currentRow}`).value = specialRemarks;
        worksheet.getCell(`A${currentRow}`).font = { name: '맑은 고딕', size: 10 };
        worksheet.getCell(`A${currentRow}`).alignment = { horizontal: 'left', vertical: 'center' };

        // ===== 빈 행 (13개 고정) =====
        currentRow++;
        const emptyRowStart = currentRow;
        for (let i = 0; i < 13; i++) {
            worksheet.mergeCells(`A${currentRow}:K${currentRow}`);
            currentRow++;
        }

        // ===== Total / Best nego Total =====
        worksheet.mergeCells(`A${currentRow}:I${currentRow}`);
        worksheet.getCell(`A${currentRow}`).value = 'Total';
        worksheet.getCell(`A${currentRow}`).font = { name: '맑은 고딕', size: 12, bold: true };
        worksheet.getCell(`A${currentRow}`).alignment = { horizontal: 'center', vertical: 'center' };
        worksheet.getCell(`A${currentRow}`).fill = {
            type: 'pattern',
            pattern: 'solid',
            fgColor: { argb: 'FFFFFFE0' }
        };
        worksheet.getCell(`A${currentRow}`).border = {
            top: { style: 'medium' },
            left: { style: 'medium' },
            bottom: { style: 'thin' }
        };
        
        // Total 행 전체 테두리
        for (let col = 2; col <= 9; col++) {
            worksheet.getCell(currentRow, col).border = {
                top: { style: 'medium' },
                bottom: { style: 'thin' }
            };
        }

        worksheet.mergeCells(`J${currentRow}:K${currentRow}`);
        worksheet.getCell(`J${currentRow}`).value = totalAmount;
        worksheet.getCell(`J${currentRow}`).numFmt = '#,##0';
        worksheet.getCell(`J${currentRow}`).font = { name: '맑은 고딕', size: 12, bold: true };
        worksheet.getCell(`J${currentRow}`).alignment = { horizontal: 'right', vertical: 'center' };
        worksheet.getCell(`J${currentRow}`).border = {
            top: { style: 'medium' },
            bottom: { style: 'thin' }
        };
        worksheet.getCell(`K${currentRow}`).border = {
            top: { style: 'medium' },
            right: { style: 'medium' },
            bottom: { style: 'thin' }
        };

        currentRow++;
        worksheet.mergeCells(`A${currentRow}:I${currentRow}`);
        worksheet.getCell(`A${currentRow}`).value = 'Best nego Total';
        worksheet.getCell(`A${currentRow}`).font = { name: '맑은 고딕', size: 12, bold: true, color: { argb: 'FFFF0000' } };
        worksheet.getCell(`A${currentRow}`).alignment = { horizontal: 'center', vertical: 'center' };
        worksheet.getCell(`A${currentRow}`).fill = {
            type: 'pattern',
            pattern: 'solid',
            fgColor: { argb: 'FFFFC7CE' }
        };
        worksheet.getCell(`A${currentRow}`).border = {
            top: { style: 'thin' },
            left: { style: 'medium' }
        };
        
        // Best nego Total 행 전체 테두리
        for (let col = 2; col <= 9; col++) {
            worksheet.getCell(currentRow, col).border = {
                top: { style: 'thin' }
            };
        }

        worksheet.mergeCells(`J${currentRow}:K${currentRow}`);
        const negoTotalValue = parseInt(document.getElementById('negoTotal')?.textContent.replace(/[^0-9]/g, '')) || totalAmount;
        worksheet.getCell(`J${currentRow}`).value = negoTotalValue;
        worksheet.getCell(`J${currentRow}`).numFmt = '#,##0';
        worksheet.getCell(`J${currentRow}`).font = { name: '맑은 고딕', size: 12, bold: true, color: { argb: 'FFFF0000' } };
        worksheet.getCell(`J${currentRow}`).alignment = { horizontal: 'right', vertical: 'center' };
        worksheet.getCell(`J${currentRow}`).border = {
            top: { style: 'thin' }
        };
        worksheet.getCell(`K${currentRow}`).border = {
            top: { style: 'thin' },
            right: { style: 'medium' }
        };
        worksheet.getRow(currentRow).height = 17.25;

        // ===== 비고 (납기/지불조건 등) =====
        currentRow++;
        const remarksStartRow = currentRow;
        
        worksheet.mergeCells(`A${currentRow}:B${currentRow + 4}`);
        worksheet.getCell(`A${currentRow}`).value = '비 고';
        worksheet.getCell(`A${currentRow}`).font = { name: '맑은 고딕', size: 11, bold: true };
        worksheet.getCell(`A${currentRow}`).alignment = { horizontal: 'center', vertical: 'center' };
        worksheet.getCell(`A${currentRow}`).fill = {
            type: 'pattern',
            pattern: 'solid',
            fgColor: { argb: 'FFFFFFE0' }
        };
        worksheet.getCell(`A${currentRow}`).border = {
            top: { style: 'medium' },
            left: { style: 'medium' },
            bottom: { style: 'medium' }
        };
        worksheet.getCell(`B${currentRow}`).border = {
            top: { style: 'medium' },
            right: { style: 'medium' },
            bottom: { style: 'medium' }
        };
        
        // 비고 좌측 셀 세로 병합 테두리
        for (let r = currentRow + 1; r <= currentRow + 4; r++) {
            worksheet.getCell(`A${r}`).border = {
                left: { style: 'medium' }
            };
            worksheet.getCell(`B${r}`).border = {
                right: { style: 'medium' }
            };
        }
        worksheet.getCell(`A${currentRow + 4}`).border = {
            left: { style: 'medium' },
            bottom: { style: 'medium' }
        };
        worksheet.getCell(`B${currentRow + 4}`).border = {
            right: { style: 'medium' },
            bottom: { style: 'medium' }
        };

        // ✅ 수정: 화면의 description_2 참조
        const generalRemarksElement = document.getElementById('remarksGeneral');
        let generalRemarksText = '';
        
        if (generalRemarksElement) {
            generalRemarksText = generalRemarksElement.innerHTML.replace(/<br\s*\/?>/gi, '\n');
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = generalRemarksText;
            generalRemarksText = tempDiv.textContent || tempDiv.innerText || '';
        }
        
        if (!generalRemarksText) {
            generalRemarksText = headerData.description_2 || '- 납기 : 협의사항\n- 지불조건 : 선급금 30%, 중도금 50%, 잔금 20%\n- 기타 : 견적유효기간 10 일';
        }

        const remarksLines = generalRemarksText.split('\n').slice(0, 5);
        while (remarksLines.length < 5) remarksLines.push('');

        for (let i = 0; i < 5; i++) {
            worksheet.mergeCells(`C${currentRow}:K${currentRow}`);
            worksheet.getCell(`C${currentRow}`).value = remarksLines[i];
            worksheet.getCell(`C${currentRow}`).font = { name: '맑은 고딕', size: 10 };
            worksheet.getCell(`C${currentRow}`).alignment = { horizontal: 'left', vertical: 'center' };
            
            // 비고 우측 테두리
            worksheet.getCell(`C${currentRow}`).border = {
                top: i === 0 ? { style: 'medium' } : undefined,
                left: { style: 'medium' }
            };
            worksheet.getCell(`K${currentRow}`).border = {
                top: i === 0 ? { style: 'medium' } : undefined,
                right: { style: 'medium' },
                bottom: i === 4 ? { style: 'medium' } : undefined
            };
            
            // 중간 컬럼들 상하 테두리만
            for (let col = 4; col <= 10; col++) {
                worksheet.getCell(currentRow, col).border = {
                    top: i === 0 ? { style: 'medium' } : undefined,
                    bottom: i === 4 ? { style: 'medium' } : undefined
                };
            }
            
            currentRow++;
        }

        // Excel 파일 생성 및 다운로드
        const buffer = await workbook.xlsx.writeBuffer();
        const blob = new Blob([buffer], { 
            type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
        });
        
        const filename = `견적서_갑지_${headerData.title || '제목없음'}_${formatDateForFilename(new Date())}.xlsx`;
        saveAs(blob, filename);
        
        console.log('[Excel] 생성 완료:', filename);
        console.log(`[Excel] 데이터 행 수: ${dataRowCount}, 총 행 수: ${currentRow}`);
        
    } catch (error) {
        console.error('[Excel] 생성 오류:', error);
        alert('Excel 파일 생성 중 오류가 발생했습니다.');
    }
}

// ============================================================================
// 유틸리티 함수
// ============================================================================

function formatDate(date) {
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    return `${year}년 ${month}월 ${day}일`;
}

function formatDateForFilename(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}${month}${day}`;
}

function formatNumber(num) {
    if (num === 0 || num === null || num === undefined) return '0';
    return num.toLocaleString('ko-KR');
}

function numberToKorean(number) {
    if (number == 0) return '일금 영원 정';
    
    const units = ['', '만', '억', '조', '경'];
    const nums = ['영', '일', '이', '삼', '사', '오', '육', '칠', '팔', '구'];
    const decimals = ['', '십', '백', '천'];
    
    let str = String(number);
    let result = '';
    let unitIndex = 0;
    
    while (str.length > 0) {
        const chunk = str.slice(-4);
        str = str.slice(0, -4);
        
        let chunkResult = '';
        for (let i = 0; i < chunk.length; i++) {
            const digit = parseInt(chunk.charAt(chunk.length - 1 - i));
            if (digit > 0) {
                chunkResult = nums[digit] + decimals[i] + chunkResult;
            }
        }
        
        if (chunkResult.length > 0) {
            result = chunkResult + units[unitIndex] + result;
        }
        unitIndex++;
    }
    
    return '일금 ' + result + '원 정';
}

function exportPDF() {
    const projectName = headerData?.title || document.getElementById('quotationTitle')?.textContent || '견적서';
    const docType = '갑지';
    const timestamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14);
    const filename = `${projectName}_${docType}_${timestamp}.pdf`;

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
        // Fallback: 서버 API 실패 시 브라우저 인쇄 기능 사용
        alert('서버 PDF 저장에 실패했습니다.\n브라우저 인쇄 기능을 사용해주세요.');
        window.print();
    });
}

function goBack() {
    if (confirm('목록으로 돌아가시겠습니까?')) {
        window.history.back();
    }
}