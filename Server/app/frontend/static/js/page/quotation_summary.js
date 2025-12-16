/**
 * 견적서 갑지 페이지 스크립트
 */

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', () => {
    console.log('견적서 갑지 페이지 로드됨');
    initSummaryPage();
    setupEventListeners();
    updateCalculations();
});

/**
 * 페이지 초기화
 */
function initSummaryPage() {
    // 날짜는 HTML에서 수동으로 설정 가능하도록 자동 설정 제거
    console.log('견적서 갑지 페이지 초기화 완료');
}

/**
 * 이벤트 리스너 설정
 */
function setupEventListeners() {
    // 편집 가능한 모든 셀에 input 이벤트 추가
    const editableCells = document.querySelectorAll('.editable');
    editableCells.forEach(cell => {
        cell.addEventListener('input', handleCellEdit);
        cell.addEventListener('blur', updateCalculations);
    });

    // Make remarks content editable
    const remarksContent = document.querySelector('.remarks-content');
    if (remarksContent) {
        remarksContent.setAttribute('contenteditable', 'true');
        remarksContent.classList.add('editable'); // Apply styling
        // Prevent enter from creating divs, maybe? Default behavior is okay for now.
    }

    // Enter 키로 다음 셀로 이동
    editableCells.forEach((cell, index) => {
        cell.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const nextCell = editableCells[index + 1];
                if (nextCell) {
                    nextCell.focus();
                }
            }
        });
    });

    // Best Nego Total 이벤트 리스너
    const negoTotal = document.getElementById('negoTotal');
    if (negoTotal) {
        negoTotal.addEventListener('blur', (e) => {
            const val = parseInt(e.target.textContent.replace(/[^0-9]/g, '')) || 0;
            if (val > 0) {
                 e.target.textContent = formatNumber(val);
            }
            updateCalculations();
        });
        negoTotal.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                negoTotal.blur();
            }
        });
    }
}

/**
 * 셀 편집 핸들러
 */
function handleCellEdit(e) {
    const cell = e.target;

    // 숫자 입력 검증 (금액 컬럼인 경우)
    if (cell.classList.contains('col-right')) {
        const value = cell.textContent.replace(/[^0-9]/g, '');
        if (value) {
            cell.textContent = formatNumber(parseInt(value));
        }
    }
}

let isFirstCalculation = true;

/**
 * 계산 업데이트
 */
function updateCalculations() {
    const tbody = document.getElementById('quotationTableBody');
    const rows = tbody.querySelectorAll('tr:not(.empty-row)');
    let total = 0;
    let subtotal = 0; // % 계산을 위한 소계

    rows.forEach((row) => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 7) {
            const unitCell = cells[4]; // 단위 셀
            const unit = unitCell.textContent.trim();
            const priceText = cells[5].textContent.replace(/[^0-9]/g, '');
            const quantityText = cells[3].textContent.replace(/[^0-9.-]/g, '');

            const price = parseInt(priceText) || 0;
            const quantity = parseFloat(quantityText) || 0;

            let amount = 0;

            // 단위가 %인 경우
            if (unit === '%') {
                // 이전 행들의 공급가액 합계에 대한 퍼센트 계산
                amount = Math.round(subtotal * (quantity / 100));
                cells[5].textContent = formatNumber(amount); // 단가도 계산된 금액으로 업데이트
                cells[6].textContent = formatNumber(amount);
            } else {
                // 일반 계산: 단가 × 수량
                amount = price * quantity;
                cells[6].textContent = formatNumber(amount);
                // % 계산을 위한 소계에 추가
                subtotal += amount;
            }

            total += amount;
        }
    });

    // 견적 총 금액 업데이트 (하단 테이블 tfoot)
    const summaryAmount = document.getElementById('summaryAmount');
    if (summaryAmount) {
        summaryAmount.textContent = formatNumber(total);
    }

    // Total 업데이트 (하단 Total 영역)
    const totalAmount = document.getElementById('totalAmount');
    if (totalAmount) {
        totalAmount.textContent = formatNumber(total);
    }

    // 상단 헤더 금액 업데이트 (Best Nego Total 우선 적용)
    const negoTotal = document.getElementById('negoTotal');
    const totalAmountVat = document.getElementById('totalAmountVat');
    const quotationAmountText = document.getElementById('quotationAmountText');
    
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

    if (totalAmountVat) {
        totalAmountVat.textContent = formatNumber(finalAmount);
    }
    
    if (quotationAmountText) {
        quotationAmountText.textContent = numberToKorean(finalAmount);
    }

    isFirstCalculation = false;
}

/**
 * 새 행 추가
 */
function addRow() {
    const tbody = document.getElementById('quotationTableBody');
    const newRow = document.createElement('tr');

    // 현재 행 수 계산 (빈 행 제외)
    const currentRows = tbody.querySelectorAll('tr:not(.empty-row)');
    const rowNumber = currentRows.length + 1;

    newRow.innerHTML = `
        <td class="col-center">${rowNumber}</td>
        <td class="col-left editable" contenteditable="true"></td>
        <td class="col-left editable" contenteditable="true"></td>
        <td class="col-center editable" contenteditable="true">1</td>
        <td class="col-center editable" contenteditable="true">식</td>
        <td class="col-right editable" contenteditable="true">0</td>
        <td class="col-right">0</td>
        <td class="col-left editable" contenteditable="true"></td>
    `;

    // 마지막 빈 행 앞에 삽입
    const emptyRows = tbody.querySelectorAll('.empty-row');
    if (emptyRows.length > 0) {
        tbody.insertBefore(newRow, emptyRows[0]);
    } else {
        tbody.appendChild(newRow);
    }

    setupEventListeners();
    updateCalculations();
}

/**
 * 행 삭제
 */
function deleteRow(rowIndex) {
    const tbody = document.getElementById('quotationTableBody');
    const rows = tbody.querySelectorAll('tr:not(.empty-row)');

    if (rows.length > 1 && confirm('이 행을 삭제하시겠습니까?')) {
        rows[rowIndex].remove();

        // 행 번호 재정렬
        renumberRows();
        updateCalculations();
    }
}

/**
 * 행 번호 재정렬
 */
function renumberRows() {
    const tbody = document.getElementById('quotationTableBody');
    const rows = tbody.querySelectorAll('tr:not(.empty-row)');

    rows.forEach((row, index) => {
        const firstCell = row.querySelector('td:first-child');
        if (firstCell) {
            firstCell.textContent = index + 1;
        }
    });
}

/**
 * 데이터 저장
 */
async function saveSummary() {
    try {
        const summaryData = collectSummaryData();

        console.log('저장할 데이터:', summaryData);

        // API 호출 (추후 구현)
        // const response = await fetch('/api/quotation/summary', {
        //     method: 'POST',
        //     headers: { 'Content-Type': 'application/json' },
        //     body: JSON.stringify(summaryData)
        // });

        // if (response.ok) {
        //     alert('저장되었습니다.');
        // } else {
        //     throw new Error('저장 실패');
        // }

        alert('저장 기능은 백엔드 API 연결 후 사용 가능합니다.');

    } catch (error) {
        console.error('저장 오류:', error);
        alert('저장 중 오류가 발생했습니다.');
    }
}

/**
 * 커버 데이터 수집
 */
function collectSummaryData() {
    const data = {
        // 기본 정보
        quotationNumber: document.getElementById('quotationNumber').value,
        quotationDate: document.getElementById('quotationDate').textContent,

        // 발신 정보
        senderCompany: document.getElementById('senderCompany').textContent,
        contractType: document.getElementById('contractType').textContent,

        // 공급자 정보
        supplierCompany: document.getElementById('supplierCompany').value,
        supplierName: document.getElementById('supplierName').value,
        businessAddress: document.getElementById('businessAddress').value,
        businessType: document.getElementById('businessType').value,
        businessNumber: document.getElementById('businessNumber').value,
        contactTel: document.getElementById('contactTel').value,
        contactEmail: document.getElementById('contactEmail').value,

        // 문서 제목
        documentTitle: document.getElementById('documentTitle').textContent,

        // 금액
        totalAmountVat: document.getElementById('totalAmountVat').textContent,
        totalAmount: document.getElementById('totalAmount').textContent,
        negoTotal: document.getElementById('negoTotal').textContent,

        // 테이블 데이터
        items: collectTableData()
    };

    return data;
}

/**
 * 테이블 데이터 수집
 */
function collectTableData() {
    const tbody = document.getElementById('quotationTableBody');
    const rows = tbody.querySelectorAll('tr:not(.empty-row)');
    const items = [];

    rows.forEach((row, index) => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 8) {
            items.push({
                no: index + 1,
                name: cells[1].textContent.trim(),
                spec: cells[2].textContent.trim(),
                quantity: cells[3].textContent.trim(),
                unit: cells[4].textContent.trim(),
                price: cells[5].textContent.replace(/[^0-9]/g, ''),
                amount: cells[6].textContent.replace(/[^0-9]/g, ''),
                remarks: cells[7].textContent.trim()
            });
        }
    });

    return items;
}

/**
 * PDF 저장
 */
function exportPDF() {
    alert('PDF 저장 기능은 추후 구현 예정입니다.\n현재는 브라우저의 인쇄 기능(Ctrl+P)을 사용해주세요.');
    window.print();
}

/**
 * 목록으로 이동
 */
function goBack() {
    if (confirm('작성 중인 내용이 있습니다. 목록으로 돌아가시겠습니까?')) {
        window.history.back();
    }
}

/**
 * 날짜 포맷 (예: 2025년 11월 26일)
 */
function formatDate(date) {
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    return `${year}년 ${month}월 ${day}일`;
}

/**
 * 날짜 포맷 (예: 2025.11.26)
 */
function formatDateShort(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}.${month}.${day}`;
}

/**
 * 숫자 포맷 (3자리 콤마)
 */
function formatNumber(num) {
    return num.toLocaleString('ko-KR');
}

/**
 * 콤마 제거
 */
function removeComma(str) {
    return str.replace(/,/g, '');
}

/**
 * 숫자를 한글 금액으로 변환 (예: 일금 일백만원 정)
 */
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
