/**
 * 견적서(을지) 상세 - Excel 및 PDF 다운로드 기능 통합 버전
 */

let detailedId = null;
let originalData = null; // 모든 데이터의 기준
let pageMode = 'view'; 

document.addEventListener('DOMContentLoaded', function() {
    const pathParts = window.location.pathname.split('/');
    detailedId = pathParts[pathParts.length - 1];

    if (detailedId) {
        loadDetailedData(detailedId);
    }

    attachCalculationListeners();
});

function attachCalculationListeners() {
    const tbody = document.querySelector('#detailedTable tbody');
    if (tbody) {
        // Remove old listener by cloning (to avoid duplicates)
        const newTbody = tbody.cloneNode(true);
        tbody.parentNode.replaceChild(newTbody, tbody);

        // input 이벤트: 계산만 업데이트 (포맷팅하지 않음)
        newTbody.addEventListener('input', function(e) {
            if (pageMode !== 'edit') return;
            const row = e.target.closest('.data-row');
            if (row && (e.target.classList.contains('edit-qty') || e.target.classList.contains('edit-price'))) {
                updateRowSubtotal(row);
                calculateGrandTotal();
            }
        });

        // blur 이벤트: 숫자 필드 포맷팅
        newTbody.addEventListener('blur', function(e) {
            if (pageMode !== 'edit') return;
            const cell = e.target;

            // 단가 필드 포맷팅
            if (cell.classList.contains('edit-price')) {
                const value = cell.textContent.replace(/[^0-9]/g, '');
                if (value) {
                    cell.textContent = formatNumber(parseInt(value));
                } else {
                    cell.textContent = '0';
                }
                // 포맷팅 후 재계산
                const row = cell.closest('.data-row');
                if (row) {
                    updateRowSubtotal(row);
                    calculateGrandTotal();
                }
            }

            // 수량 필드 포맷팅
            if (cell.classList.contains('edit-qty')) {
                const value = cell.textContent.replace(/[^0-9]/g, '');
                if (value) {
                    cell.textContent = value; // 수량은 쉼표 없이 표시
                } else {
                    cell.textContent = '0';
                }
                // 포맷팅 후 재계산
                const row = cell.closest('.data-row');
                if (row) {
                    updateRowSubtotal(row);
                    calculateGrandTotal();
                }
            }
        }, true);
    }
}

// 데이터 로드
async function loadDetailedData(id) {
    try {
        const response = await fetch(`/api/v1/quotation/detailed/${id}`);
        if (!response.ok) throw new Error('데이터 로드 실패');
        originalData = await response.json();

        // 제목 설정
        const pageTitle = document.getElementById('pageTitle');
        if (pageTitle && originalData.title) {
            pageTitle.textContent = originalData.title;
        }

        renderDetailedTable(originalData.detailed_resources);
        document.getElementById('quotationDescription').innerText = originalData.description || '';

        document.getElementById('loading').style.display = 'none';
        document.getElementById('detailedTable').style.display = 'table';
        toggleEditMode('view');
    } catch (error) {
        console.error(error);
        alert('데이터를 불러오는데 실패했습니다.');
    }
}

// ============================================================================
// [신규] Excel 다운로드 (갑지와 동일한 API 호출 방식)
// ============================================================================
async function exportDetailedToExcel() {
    console.log('[Excel] 을지 API 호출 시작');
    
    if (!detailedId) {
        alert('견적서 ID가 없습니다.');
        return;
    }

    try {
        const response = await fetch(`/api/v1/export/excel/detailed/${detailedId}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            }
        });

        if (!response.ok) {
            throw new Error(`Excel 생성 실패: ${response.status}`);
        }

        const blob = await response.blob();
        
        // 파일명 생성 (갑지 로직과 동일하게 타임스탬프 적용)
        const timestamp = formatDateForFilename(new Date());
        const projectName = originalData?.detailed?.name || '상세견적서_을지';
        const filename = `${projectName}_${timestamp}.xlsx`;
        
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
// [신규] PDF 저장 및 인쇄 (갑지와 동일한 로직)
// ============================================================================
async function exportToPDF() {
    const projectName = originalData?.title || '상세견적서';
    const docType = '을지';
    const timestamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14);
    const filename = `${projectName}_${docType}_${timestamp}.pdf`;

    // 💡 폴더 정보 가져오기 (1번의 API 호출로 최적화)
    let generalName = '';
    let folderTitle = '';

    if (originalData?.folder_id) {
        try {
            const folderRes = await fetch(`/api/v1/quotation/folder/${originalData.folder_id}`);
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
        // 서버 실패 시 브라우저 인쇄창 띄움 (Fallback)
        window.print();
    });
}

// ============================================================================
// 유틸리티 함수 (갑지 코드와 동일하게 추가)
// ============================================================================
function formatDateForFilename(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}${month}${day}`;
}

// ============================================================================
// 기존 테이블 제어 및 UI 로직 (유지)
// ============================================================================

function toggleEditMode(mode) {
    pageMode = mode;
    const table = document.getElementById('detailedTable');
    const viewActions = document.getElementById('viewActions');
    const editActions = document.getElementById('editActions');
    const descriptionBox = document.getElementById('quotationDescription');
    const titleEl = document.getElementById('pageTitle');

    table.dataset.mode = mode;
    const editableCells = table.querySelectorAll('.edit-qty, .edit-unit, .edit-price, .edit-desc');
    editableCells.forEach(cell => cell.contentEditable = (mode === 'edit'));
    descriptionBox.contentEditable = (mode === 'edit');

    // 제목 수정 가능하도록 설정
    if (titleEl) {
        titleEl.contentEditable = (mode === 'edit') ? "true" : "false";
        if (mode === 'edit') {
            titleEl.style.background = '#fffbeb';
            titleEl.style.outline = '1.5px dashed #f59e0b';
        } else {
            titleEl.style.background = '';
            titleEl.style.outline = '';
        }
    }

    if (mode === 'edit') {
        viewActions.style.display = 'none';
        editActions.style.display = 'flex';
    } else {
        viewActions.style.display = 'flex';
        editActions.style.display = 'none';
        if (originalData) {
            renderDetailedTable(originalData.detailed_resources);
            descriptionBox.innerText = originalData.description || '';
            if (titleEl && originalData.title) {
                titleEl.textContent = originalData.title;
            }
        }
    }
}

function renderDetailedTable(resources) {
    const tbody = document.querySelector('#detailedTable tbody');
    tbody.innerHTML = '';
    const majorOrder = ['자재비', '인건비', '출장경비', '관리비'];
    const groups = groupByMajorThenMachine(resources);
    let html = '';
    let rowNo = 1;

    const renderSection = (major) => {
        const machines = groups[major];
        let majorTotal = 0;
        // 표시용 major명 (출장경비 -> 출장 경비로 공백 추가)
        const displayMajor = major === '출장경비' ? '출장 경비' : major;
        html += `<tr class="section-title-row"><td colspan="8">■ ${displayMajor} 상세 내역</td></tr>`;
        Object.keys(machines).forEach(machineName => {
            const items = machines[machineName];
            items.forEach((item, idx) => {
                const subtotal = (item.compare || 0) * (item.solo_price || 0);
                majorTotal += subtotal;
                html += `
                <tr class="data-row" data-machine="${item.machine_name}" data-major="${item.major}" data-minor="${item.minor}">
                    <td class="text-center">${rowNo++}</td>
                    ${idx === 0 ? `<td rowspan="${items.length}" class="machine-name-cell text-center">${machineName}</td>` : ''}
                    <td>${item.minor}</td>
                    <td class="edit-qty text-right">${item.compare}</td>
                    <td class="edit-unit text-center">${item.unit || '식'}</td>
                    <td class="edit-price text-right">${formatNumber(item.solo_price)}</td>
                    <td class="row-subtotal text-right">${formatNumber(subtotal)}</td>
                    <td class="edit-desc">${item.description || ''}</td>
                </tr>`;
            });
        });
        html += `<tr class="major-subtotal-row"><td colspan="6" class="text-center">${displayMajor} 총 합계</td><td class="text-right font-bold">${formatNumber(majorTotal)}</td><td></td></tr>`;
    };

    // majorOrder 순서대로 렌더링
    majorOrder.forEach(major => {
        if (groups[major]) renderSection(major);
    });
    tbody.innerHTML = html;
    calculateGrandTotal();

    // Re-attach event listeners after innerHTML update
    attachCalculationListeners();
}

function groupByMajorThenMachine(res) {
    return res.reduce((acc, curr) => {
        const major = curr.major || '기타';
        const machine = curr.machine_name || '미분류';
        if (!acc[major]) acc[major] = {};
        if (!acc[major][machine]) acc[major][machine] = [];
        acc[major][machine].push(curr);
        return acc;
    }, {});
}

function updateRowSubtotal(row) {
    const qtyCell = row.querySelector('.edit-qty');
    const priceCell = row.querySelector('.edit-price');
    const subtotalCell = row.querySelector('.row-subtotal');

    if (qtyCell && priceCell && subtotalCell) {
        const qty = parseNumber(qtyCell.textContent);
        const price = parseNumber(priceCell.textContent);
        const subtotal = qty * price;
        subtotalCell.textContent = formatNumber(subtotal);
    }
}

function calculateGrandTotal() {
    let total = 0;

    // 각 major 섹션별로 소계 계산 및 업데이트
    const majorOrder = ['자재비', '인건비', '출장경비', '관리비'];
    majorOrder.forEach(major => {
        let majorTotal = 0;
        const displayMajor = major === '출장경비' ? '출장 경비' : major;

        // 해당 major의 모든 row-subtotal 합산
        document.querySelectorAll(`.data-row[data-major="${major}"] .row-subtotal`).forEach(cell => {
            majorTotal += parseNumber(cell.textContent);
        });

        // major-subtotal-row 찾아서 업데이트
        const majorSubtotalRows = document.querySelectorAll('.major-subtotal-row');
        majorSubtotalRows.forEach(row => {
            const labelCell = row.querySelector('td:first-child');
            if (labelCell && labelCell.textContent.includes(`${displayMajor} 총 합계`)) {
                const amountCell = row.querySelector('td:nth-child(2)');
                if (amountCell) {
                    amountCell.textContent = formatNumber(majorTotal);
                }
            }
        });

        total += majorTotal;
    });

    // 전체 합계 업데이트
    const tfoot = document.querySelector('#detailedTable tfoot');
    if (tfoot) {
        tfoot.innerHTML = `<tr class="total-row"><td colspan="6" class="text-center">합 계 (VAT 별도)</td><td class="total-amount-cell text-right font-bold">${formatNumber(total)}</td><td></td></tr>`;
    }
}

async function saveDetailedData() {
    const rows = document.querySelectorAll('.data-row');
    const resources = Array.from(rows).map(row => ({
        machine_name: row.dataset.machine,
        major: row.dataset.major,
        minor: row.dataset.minor,
        unit: row.querySelector('.edit-unit').textContent.trim(),
        compare: parseNumber(row.querySelector('.edit-qty').textContent),
        solo_price: parseNumber(row.querySelector('.edit-price').textContent),
        description: row.querySelector('.edit-desc').textContent.trim()
    }));

    const title = document.getElementById('pageTitle')?.textContent.trim() || originalData.title;

    const payload = {
        title: title,
        creator: originalData.creator,
        description: document.getElementById('quotationDescription').innerText.trim(),
        detailed_resources: resources
    };

    if (!confirm('변경사항을 저장하시겠습니까?')) return;
    try {
        const response = await fetch(`/api/v1/quotation/detailed/${detailedId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (response.ok) {
            originalData = await response.json();
            alert('성공적으로 저장되었습니다.');
            toggleEditMode('view');
        }
    } catch (e) { alert('저장 실패'); }
}

function formatNumber(n) { return (n || 0).toLocaleString('ko-KR'); }
function parseNumber(s) { return parseInt(s?.toString().replace(/[^0-9]/g, '')) || 0; }
function goBack() { if (confirm('목록으로 돌아가시겠습니까?')) window.history.back(); }

/**
 * 갑지 생성 모달 열기
 */
function openHeaderCreateModal() {
    const modal = document.getElementById('headerCreateModal');
    if (modal) {
        modal.style.display = 'flex';
        // 제목과 작성자 자동 채우기
        document.getElementById('headerTitle').value = originalData?.title || '';
        document.getElementById('headerCreator').value = originalData?.creator || '';
        document.getElementById('headerClient').value = '';
        document.getElementById('headerManufacturer').value = '';
        document.getElementById('headerPicName').value = '';
        document.getElementById('headerPicPosition').value = '';
    }
}

/**
 * 갑지 생성 모달 닫기
 */
function closeHeaderCreateModal() {
    const modal = document.getElementById('headerCreateModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * 모달에서 갑지 생성
 */
async function createHeaderFromModal() {
    const title = document.getElementById('headerTitle').value.trim();
    const creator = document.getElementById('headerCreator').value.trim();
    const client = document.getElementById('headerClient').value.trim();
    const manufacturer = document.getElementById('headerManufacturer').value.trim();
    const picName = document.getElementById('headerPicName').value.trim();
    const picPosition = document.getElementById('headerPicPosition').value.trim();

    // 필수 필드 검증
    if (!title) {
        alert('제목을 입력해주세요.');
        document.getElementById('headerTitle').focus();
        return;
    }
    if (!creator) {
        alert('작성자를 입력해주세요.');
        document.getElementById('headerCreator').focus();
        return;
    }
    if (!client) {
        alert('고객사를 입력해주세요.');
        document.getElementById('headerClient').focus();
        return;
    }
    if (!picName) {
        alert('담당자명을 입력해주세요.');
        document.getElementById('headerPicName').focus();
        return;
    }
    if (!picPosition) {
        alert('담당자 직급을 입력해주세요.');
        document.getElementById('headerPicPosition').focus();
        return;
    }

    if (!originalData || !originalData.folder_id) {
        alert('폴더 정보를 찾을 수 없습니다.');
        return;
    }

    if (!detailedId) {
        alert('을지 ID를 찾을 수 없습니다.');
        return;
    }

    const requestData = {
        folder_id: originalData.folder_id,
        detailed_id: detailedId,
        title: title,
        creator: creator,
        client: client,
        manufacturer: manufacturer || null,
        pic_name: picName,
        pic_position: picPosition
    };

    try {
        const response = await fetch('/api/v1/quotation/header', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '갑지 생성 실패');
        }

        const result = await response.json();
        alert('갑지가 성공적으로 생성되었습니다.');
        closeHeaderCreateModal();

        // 생성된 갑지 상세 페이지로 이동
        location.href = `/service/quotation/general/header/detail/${result.id}`;
    } catch (error) {
        console.error('갑지 생성 오류:', error);
        alert('갑지 생성 중 오류가 발생했습니다: ' + error.message);
    }
}

// 모달 외부 클릭 시 닫기
window.addEventListener('click', function(event) {
    const modal = document.getElementById('headerCreateModal');
    if (event.target === modal) {
        closeHeaderCreateModal();
    }
});

async function createHeaderFromDetailed() {
    if (!detailedId || !originalData) {
        alert('데이터가 로드되지 않았습니다.');
        return;
    }
    try {
        const res = await fetch(`/api/v1/quotation/detailed/${detailedId}`);
        if (res.ok) {
            const data = await res.json();
            if (data.folder_id) {
                location.href = `/service/quotation/general/header/register?folder_id=${data.folder_id}`;
            } else {
                alert('Folder ID를 찾을 수 없습니다.');
            }
        }
    } catch (e) {
        console.error(e);
        alert('갑지 만들기 페이지로 이동 중 오류가 발생했습니다.');
    }
}