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
    renderTable(data.header_resources || []);
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
        const docTitle = document.getElementById('documentTitle');
        const quotTitle = document.getElementById('quotationTitle');
        if (docTitle) docTitle.textContent = data.title;
        if (quotTitle) quotTitle.textContent = data.title;

        // 제목 양방향 동기화 - documentTitle과 quotationTitle 모두
        if (docTitle && quotTitle) {
            // documentTitle 변경 시 quotationTitle 업데이트
            docTitle.addEventListener('input', () => {
                quotTitle.textContent = docTitle.textContent;
            });
            // quotationTitle 변경 시 documentTitle 업데이트
            quotTitle.addEventListener('input', () => {
                docTitle.textContent = quotTitle.textContent;
            });
        }
    }

    // 담당자명과 직급 필드 분리
    const picName = document.getElementById('picName');
    const picPosition = document.getElementById('picPosition');
    if (picName) picName.textContent = data.pic_name || '';
    if (picPosition) picPosition.textContent = data.pic_position || '';

    // Best nego Total 로드
    const negoTotal = document.getElementById('negoTotal');
    if (negoTotal && data.best_nego_total) {
        negoTotal.textContent = formatNumber(data.best_nego_total);
        isFirstCalculation = false; // 저장된 값이 있으면 자동 계산 방지
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

    if (!resources || resources.length === 0) {
        html = '<tr><td colspan="9" style="text-align: center; padding: 20px;">데이터가 없습니다</td></tr>';
        tbody.innerHTML = html;
        return;
    }

    // 1. 경비와 안전관리비 및 기업이윤을 하단으로 이동하기 위해 정렬
    const sortedResources = [...resources].sort((a, b) => {
        const aIsBottom = a.name === '경비' || a.name === '안전관리비 및 기업이윤';
        const bIsBottom = b.name === '경비' || b.name === '안전관리비 및 기업이윤';

        if (aIsBottom && !bIsBottom) return 1;  // a를 뒤로
        if (!aIsBottom && bIsBottom) return -1; // b를 뒤로

        // 경비와 안전관리비 사이의 순서 (경비 먼저, 안전관리비 나중)
        if (aIsBottom && bIsBottom) {
            if (a.name === '경비') return -1;
            if (b.name === '경비') return 1;
        }

        return 0; // 원래 순서 유지
    });

    // 2. 장비명별로 그룹화하여 rowspan 계산
    const machineGroups = {};
    sortedResources.forEach(item => {
        const machine = item.machine || '';
        if (!machineGroups[machine]) {
            machineGroups[machine] = [];
        }
        machineGroups[machine].push(item);
    });

    // 3. 테이블 렌더링
    let rowNumber = 1;
    sortedResources.forEach((item, index) => {
        const machine = item.machine || '';
        const quantity = item.compare || 1;
        const unit = item.unit || '식';
        const price = item.solo_price || 0;
        const subtotal = item.subtotal || (price * quantity);

        html += `<tr data-machine="${machine}" data-item-name="${item.name || ''}">`;
        html += `<td class="col-no col-center">${rowNumber}</td>`;

        // 장비명 셀 - 같은 장비명의 첫 번째 행에만 표시하고 rowspan 적용
        const isFirstInGroup = index === 0 || sortedResources[index - 1].machine !== machine;
        if (isFirstInGroup) {
            const groupSize = machineGroups[machine].length;
            html += `<td class="col-machine col-center" rowspan="${groupSize}" style="vertical-align: middle;">${machine}</td>`;
        }

        html += `<td class="col-name col-center" data-original-name="${item.name || ''}">${item.name || ''}</td>`;
        html += `<td class="col-spec col-center" contenteditable="true">${item.spac || ''}</td>`;
        html += `<td class="col-quantity col-center" contenteditable="true">${quantity}</td>`;
        html += `<td class="col-unit col-center" contenteditable="true">${unit}</td>`;
        html += `<td class="col-price col-right" contenteditable="true">${formatNumber(price)}</td>`;
        html += `<td class="col-unit-price col-right">${formatNumber(subtotal)}</td>`;
        html += `<td class="col-remarks col-left" contenteditable="true">${item.description || ''}</td>`;
        html += `</tr>`;

        rowNumber++;
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
    // 테이블 tbody에 이벤트 위임 방식 사용
    const tbody = document.getElementById('quotationTableBody');
    if (tbody) {
        tbody.addEventListener('input', (e) => {
            if (e.target.contentEditable === 'true') {
                handleCellEdit(e);
                updateCalculations();
            }
        });
    }

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

    // Best nego Total 이벤트 리스너 복원
    const negoTotal = document.getElementById('negoTotal');
    if (negoTotal) {
        negoTotal.addEventListener('input', () => {
            updateCalculations();
        });
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

    // Best nego Total 로직 복원
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

// 한글 금액 변환 (화면 표시용)
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
    const title = document.getElementById('documentTitle').textContent || document.getElementById('quotationTitle').textContent;
    const negoTotal = document.getElementById('negoTotal');
    const bestNegoTotal = negoTotal ? parseInt(negoTotal.textContent.replace(/[^0-9]/g, '')) || 0 : 0;

    return {
        title: title,
        client: document.getElementById('senderCompany').textContent,
        pic_name: document.getElementById('picName').textContent.trim(),
        pic_position: document.getElementById('picPosition').textContent.trim(),
        description_1: document.getElementById('remarksSpecial').textContent,
        description_2: document.getElementById('remarksGeneral').textContent || document.getElementById('remarksGeneral').innerHTML.replace(/<br>/g, '\n'),
        best_nego_total: bestNegoTotal,
        header_resources: collectTableData()
    };
}

function collectTableData() {
    const tbody = document.getElementById('quotationTableBody');
    const rows = tbody.querySelectorAll('tr:not(.empty-row)');
    const items = [];

    rows.forEach((row, index) => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 8) {  // 장비명이 rowspan이라 셀 개수가 다를 수 있음
            // data-machine 속성에서 장비명 가져오기
            const machine = row.getAttribute('data-machine') || '';

            // 셀 인덱스 조정 - 장비명 셀이 있는지 확인
            const hasMachineCell = cells[1]?.classList.contains('col-machine');
            const nameIndex = hasMachineCell ? 2 : 1;
            const specIndex = hasMachineCell ? 3 : 2;
            const quantityIndex = hasMachineCell ? 4 : 3;
            const unitIndex = hasMachineCell ? 5 : 4;
            const priceIndex = hasMachineCell ? 6 : 5;
            const remarksIndex = hasMachineCell ? 8 : 7;

            items.push({
                machine: machine,
                name: cells[nameIndex].textContent.trim(),
                spac: cells[specIndex].textContent.trim(),
                compare: parseInt(cells[quantityIndex].textContent.replace(/[^0-9]/g, '')) || 1,
                unit: cells[unitIndex].textContent.trim(),
                solo_price: parseInt(cells[priceIndex].textContent.replace(/[^0-9]/g, '')) || 0,
                description: cells[remarksIndex].textContent.trim()
            });
        }
    });

    return items;
}

// ============================================================================
// Excel 다운로드 (API 호출)
// ============================================================================

async function exportHeaderToExcel() {
    console.log('[Excel] API 호출 시작');
    
    if (!headerId) {
        alert('견적서 ID가 없습니다.');
        return;
    }

    try {
        const response = await fetch(`/api/v1/export/excel/header/${headerId}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            }
        });

        if (!response.ok) {
            throw new Error(`Excel 생성 실패: ${response.status}`);
        }

        // Blob으로 변환
        const blob = await response.blob();
        
        // 파일명 생성
        const timestamp = formatDateForFilename(new Date());
        const title = headerData?.title || '견적서';
        const filename = `견적서_갑지_${title}_${timestamp}.xlsx`;
        
        // 다운로드
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        console.log('[Excel] 다운로드 완료:', filename);
        
    } catch (error) {
        console.error('[Excel] 다운로드 오류:', error);
        alert('Excel 파일 다운로드 중 오류가 발생했습니다.');
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

async function exportToPDF() {
    const projectName = headerData?.title || document.getElementById('quotationTitle')?.textContent || '견적서';
    const docType = '갑지';
    const timestamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14);
    const filename = `${projectName}_${docType}_${timestamp}.pdf`;

    // 💡 폴더 정보 가져오기 (1번의 API 호출로 최적화)
    let generalName = '';
    let folderTitle = '';

    if (headerData?.folder_id) {
        try {
            const folderRes = await fetch(`/api/v1/quotation/folder/${headerData.folder_id}`);
            if (folderRes.ok) {
                const folderData = await folderRes.json();
                folderTitle = folderData.title || '';
                generalName = folderData.general_name || '';  // 폴더 API에서 바로 가져옴
            }
        } catch (err) {
            console.error('폴더 정보 조회 오류:', err);
        }
    }

    fetch('/api/save-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            url: window.location.href,
            filename: filename,
            projectName: projectName,
            docType: docType,
            generalName: generalName,
            folderTitle: folderTitle
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