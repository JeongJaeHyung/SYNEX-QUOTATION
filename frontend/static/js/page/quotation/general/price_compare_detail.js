/**
 * 내정가 견적 비교 상세 - Excel 및 PDF 서버 API 연동 통합본
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

    setupCalculationEvents();
});

// ============================================================================
// 1. 데이터 로드
// ============================================================================
async function loadPriceCompareData(id) {
    const loading = document.getElementById('loading');
    try {
        if (loading) loading.style.display = 'block';
        const response = await fetch(`/api/v1/quotation/price_compare/${id}`);
        if (!response.ok) throw new Error('데이터 로드 실패');
        
        priceCompareData = await response.json();

        document.getElementById('creatorName').textContent = priceCompareData.creator || '-';
        document.getElementById('createdDate').textContent = priceCompareData.created_at?.substring(0, 10) || '-';

        // 제목 설정
        const pageTitle = document.getElementById('pageTitle');
        if (pageTitle && priceCompareData.title) {
            pageTitle.textContent = priceCompareData.title;
        }

        initUIByMode();
        renderComparisonTable(priceCompareData.price_compare_resources);

        const notesSection = document.getElementById('notesSection');
        if (notesSection) notesSection.style.display = 'block';

    } catch (error) {
        console.error('Load Error:', error);
    } finally {
        if (loading) loading.style.display = 'none';
    }
}

// ============================================================================
// 2. [신규/수정] Excel 다운로드 (서버 API 호출 방식)
// ============================================================================
async function exportToExcel() {
    console.log('[Excel] 내정가 비교 API 호출 시작');
    
    if (!priceCompareId) {
        alert('견적서 ID가 없습니다.');
        return;
    }

    try {
        const response = await fetch(`/api/v1/export/excel/price_compare/${priceCompareId}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            }
        });

        if (!response.ok) {
            throw new Error(`Excel 생성 실패: ${response.status}`);
        }

        const blob = await response.blob();
        
        // 파일명 생성
        const timestamp = formatDateForFilename(new Date());
        const projectName = priceCompareData?.description || '내정가견적비교';
        const filename = `${projectName}_비교서_${timestamp}.xlsx`;
        
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
// 3. [수정] PDF 내보내기 (서버 API 사용 일원화)
// ============================================================================
async function exportToPDF() {
    const projectName = priceCompareData?.title || '비교견적';
    const docType = '내정가_견적가_비교';
    const timestamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14);
    const filename = `${projectName}_${docType}_${timestamp}.pdf`;

    // 💡 폴더 정보 가져오기 (1번의 API 호출로 최적화)
    let generalName = '';
    let folderTitle = '';

    if (priceCompareData?.folder_id) {
        try {
            const folderRes = await fetch(`/api/v1/quotation/folder/${priceCompareData.folder_id}`);
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
        window.print(); // 서버 실패 시 기본 인쇄창
    });
}

// ============================================================================
// 4. 공통 유틸리티
// ============================================================================
function formatDateForFilename(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}${month}${day}`;
}

// ============================================================================
// 5. 기존 UI 및 계산 로직 (유지)
// ============================================================================
function initUIByMode() {
    const isEdit = (pageMode === 'edit');
    const footer = document.getElementById('actionFooter');
    const notes = document.getElementById('notesContent');
    const controls = document.getElementById('controlsContainer');
    const titleEl = document.getElementById('pageTitle');
    const sideMenu = document.getElementById('sideActionMenu');

    // 제목 수정 가능하도록 설정
    if (titleEl) {
        titleEl.contentEditable = isEdit ? "true" : "false";
        if (isEdit) {
            titleEl.style.background = '#fffbeb';
            titleEl.style.outline = '1.5px dashed #f59e0b';
        } else {
            titleEl.style.background = '';
            titleEl.style.outline = '';
        }
    }

    if (notes) {
        notes.textContent = priceCompareData.description || '';
        notes.contentEditable = isEdit ? "true" : "false";
        if (isEdit) notes.classList.add('editable-cell');
        else notes.classList.remove('editable-cell');
    }

    if (controls) controls.style.display = isEdit ? 'flex' : 'none';

    // 하단 footer는 항상 숨김 (사이드바로 이동)
    if (footer) {
        footer.style.display = 'none';
    }

    // 사이드 메뉴는 항상 표시하되, 편집 모드에 따라 버튼 구성 변경
    if (sideMenu) {
        sideMenu.style.display = 'flex';
        if (isEdit) {
            // 편집 모드: 저장/취소 버튼만 표시
            sideMenu.innerHTML = `
                <button class="btn btn-secondary" onclick="location.href='?mode=view'">취소</button>
                <button class="btn btn-primary" onclick="saveChanges()">저장</button>`;
        } else {
            // 보기 모드: 기존 버튼들 표시
            sideMenu.innerHTML = `
                <button class="btn btn-secondary" onclick="window.history.back()">목록으로</button>
                <button class="btn btn-warning" onclick="toggleEditMode('edit')">수정하기</button>
                <button class="btn btn-success" onclick="exportToExcel()">Excel 저장</button>
                <button class="btn btn-outline" onclick="exportToPDF()">PDF 저장</button>
                <button class="btn btn-outline" onclick="openDetailedCreateModal()">📑 을지 만들기</button>`;
        }
    }
}

function renderComparisonTable(resources) {
    const tbody = document.getElementById('comparisonTableBody');
    if (!tbody) return;
    const isEdit = (pageMode === 'edit');
    tbody.innerHTML = '';

    const groups = groupByMajorThenMachine(resources);
    const majorOrder = ["자재비", "인건비", "출장경비", "관리비"];
    const sortedMajors = Object.keys(groups).sort((a, b) => {
        // "경비"를 "출장경비"로 매핑
        const getMappedMajor = (major) => major === "경비" ? "출장경비" : major;
        const indexA = majorOrder.indexOf(getMappedMajor(a));
        const indexB = majorOrder.indexOf(getMappedMajor(b));
        return (indexA === -1 ? 99 : indexA) - (indexB === -1 ? 99 : indexB);
    });

    let html = '';
    sortedMajors.forEach(major => {
        const machineGroups = groups[major];
        let majorRowCount = Object.values(machineGroups).reduce((acc, curr) => acc + curr.length, 0) + 1;
        let isFirstMajorRow = true;
        // 표시용 major명 (경비 -> 출장경비)
        const displayMajor = major === '경비' ? '출장경비' : major;
        Object.keys(machineGroups).forEach(machineName => {
            const items = machineGroups[machineName];
            items.forEach((item, idx) => {
                html += `<tr class="category-row" data-major="${major}" data-machine-id="${item.machine_id}" data-machine-name="${machineName}">`;
                if (isFirstMajorRow) { html += `<td rowspan="${majorRowCount}" class="category-cell"><strong>${displayMajor}</strong></td>`; isFirstMajorRow = false; }
                if (idx === 0) html += `<td rowspan="${items.length}" class="machine-name-cell"><strong>${machineName}</strong></td>`;
                // 출장경비(경비)의 교통비, 숙박비, 식대는 M/D 단위 강제, 운송비는 제외
                const isExpenseItem = (major === '경비' && ['교통비', '숙박비', '식대'].includes(item.minor));
                const quotationUnit = isExpenseItem ? 'M/D' : (item.quotation_unit || '식');

                // 관리비는 내정가를 0으로 설정
                const costPrice = major === '관리비' ? 0 : item.cost_solo_price;

                html += `
                    <td class="minor-name">${item.minor || ''}</td>
                    <td class="cost-qty">${item.cost_compare || 0}</td>
                    <td>식</td>
                    <td class="cost-price">${formatNumber(costPrice)}</td>
                    <td class="cost-amount">0</td>
                    <td class="quote-qty ${isEdit ? 'editable-cell' : ''}" ${isEdit ? 'contenteditable="true"' : ''}>${item.quotation_compare || 0}</td>
                    <td class="quote-unit ${isEdit ? 'editable-cell' : ''}" ${isEdit ? 'contenteditable="true"' : ''}>${quotationUnit}</td>
                    <td class="quote-price ${isEdit ? 'editable-cell' : ''}" ${isEdit ? 'contenteditable="true"' : ''}>${formatNumber(item.quotation_solo_price)}</td>
                    <td class="row-upper ${isEdit && major !== '관리비' ? 'editable-cell' : ''}" ${isEdit && major !== '관리비' ? 'contenteditable="true"' : ''}>${major === '관리비' ? '-' : (item.upper || 0)}</td>
                    <td class="quote-amount">0</td>
                    <td class="row-note ${isEdit ? 'editable-cell' : ''}" ${isEdit ? 'contenteditable="true"' : ''}>${item.description || ''}</td>
                </tr>`;
            });
        });
        html += `<tr class="subtotal-row" data-subtotal-major="${major}"><td colspan="2">${displayMajor} 소계</td><td colspan="3"></td><td class="cost-subtotal">0</td><td colspan="4"></td><td class="quote-subtotal">0</td><td class="difference-cell">0</td></tr>`;
    });
    html += `<tr class="final-total-row"><td colspan="6">TOTAL</td><td class="cost-final-total">0</td><td colspan="4"></td><td class="final-total-cell quote-final-total">0</td><td class="difference-cell">0</td></tr>
             <tr class="markup-row"><td colspan="11"></td><td class="margin-cell">0 %</td><td class="markup-cell">이익률</td></tr>`;
    tbody.innerHTML = html;
    calculateAllTotals();
}

async function saveChanges() {
    if (!priceCompareId || !priceCompareData) return;
    if (!confirm('현재 수정된 내용을 저장하시겠습니까?')) return;
    const resources = [];
    document.querySelectorAll('tr.category-row').forEach(row => {
        resources.push({
            "machine_id": row.dataset.machineId, "machine_name": row.dataset.machineName, "major": row.dataset.major,
            "minor": row.querySelector('.minor-name')?.textContent.trim(),
            "cost_solo_price": parseNumber(row.querySelector('.cost-price')?.textContent), "cost_unit": "식", "cost_compare": parseNumber(row.querySelector('.cost-qty')?.textContent),
            "quotation_solo_price": parseNumber(row.querySelector('.quote-price')?.textContent),
            "quotation_unit": row.querySelector('.quote-unit')?.textContent.trim() || "식",
            "quotation_compare": parseNumber(row.querySelector('.quote-qty')?.textContent),
            "upper": parseFloat(row.querySelector('.row-upper')?.textContent) || 0, "description": row.querySelector('.row-note')?.textContent.trim() || ""
        });
    });
    const title = document.getElementById('pageTitle')?.textContent.trim() || priceCompareData.title;
    const payload = { "title": title, "creator": document.getElementById('creatorName').textContent.trim(), "description": document.getElementById('notesContent').textContent.trim(), "machine_ids": priceCompareData.machine_ids, "price_compare_resources": resources };
    const res = await fetch(`/api/v1/quotation/price_compare/${priceCompareId}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    if (res.ok) { alert('저장되었습니다.'); location.href = '?mode=view'; }
}

function setupCalculationEvents() {
    const tbody = document.getElementById('comparisonTableBody');
    if (!tbody) return;

    // 일괄상승률 입력 이벤트
    const markupInput = document.getElementById('markup-rate');
    if (markupInput) {
        markupInput.addEventListener('input', () => {
            const rate = parseFloat(markupInput.value) || 0;
            document.querySelectorAll('tr.category-row').forEach(row => {
                const major = row.dataset.major;
                // 관리비는 일괄상승률 적용 안함
                if (major === '관리비') return;

                const costP = parseNumber(row.querySelector('.cost-price').textContent);
                row.querySelector('.row-upper').textContent = rate;
                row.querySelector('.quote-price').textContent = formatNumber(Math.round(costP * (1 + rate / 100)));
            });
            calculateAllTotals();
        });
    }

    tbody.addEventListener('input', (e) => {
        const row = e.target.closest('tr'); if (!row?.classList.contains('category-row')) return;
        if (e.target.classList.contains('row-upper')) {
            const costP = parseNumber(row.querySelector('.cost-price').textContent);
            const rate = parseFloat(e.target.textContent) || 0;
            row.querySelector('.quote-price').textContent = formatNumber(Math.round(costP * (1 + rate / 100)));
        } else if (e.target.classList.contains('quote-price')) {
            const costP = parseNumber(row.querySelector('.cost-price').textContent);
            const quoteP = parseNumber(e.target.textContent);
            if (costP > 0) row.querySelector('.row-upper').textContent = ((quoteP - costP) / costP * 100).toFixed(1);
        }
        calculateAllTotals();
    });
}

function calculateAllTotals() {
    let tCost = 0, tQuote = 0; const majorTotals = {};

    // 1단계: 관리비를 제외한 모든 항목의 합계 먼저 계산 (자재비+인건비+경비)
    let sumExcludingManagement = 0;
    document.querySelectorAll('tr.category-row').forEach(row => {
        const major = row.dataset.major;
        if (major !== '관리비') {
            const qp = parseNumber(row.querySelector('.quote-price').textContent);
            const qq = parseNumber(row.querySelector('.quote-qty').textContent);
            sumExcludingManagement += qp * qq;
        }
    });

    // 2단계: 관리비 단가 자동 설정 후 전체 계산
    document.querySelectorAll('tr.category-row').forEach(row => {
        const major = row.dataset.major;
        if (!majorTotals[major]) majorTotals[major] = { c: 0, q: 0 };

        const cp = parseNumber(row.querySelector('.cost-price').textContent);
        const cq = parseNumber(row.querySelector('.cost-qty').textContent);
        let qp = parseNumber(row.querySelector('.quote-price').textContent);
        const qq = parseNumber(row.querySelector('.quote-qty').textContent);

        // 관리비(일반관리비, 기업이윤)는 단가를 자동 계산
        if (major === '관리비') {
            qp = Math.round(sumExcludingManagement / 100);
            row.querySelector('.quote-price').textContent = formatNumber(qp);
        }

        const camt = cp * cq, qamt = qp * qq;
        row.querySelector('.cost-amount').textContent = formatNumber(camt);
        row.querySelector('.quote-amount').textContent = formatNumber(qamt);
        majorTotals[major].c += camt; majorTotals[major].q += qamt;
    });

    document.querySelectorAll('.subtotal-row').forEach(row => {
        const t = majorTotals[row.dataset.subtotalMajor] || { c: 0, q: 0 };
        row.querySelector('.cost-subtotal').textContent = formatNumber(t.c);
        row.querySelector('.quote-subtotal').textContent = formatNumber(t.q);
        row.querySelector('.difference-cell').textContent = formatNumber(t.q - t.c);
        tCost += t.c; tQuote += t.q;
    });
    const fr = document.querySelector('.final-total-row');
    if (fr) {
        fr.querySelector('.cost-final-total').textContent = formatNumber(tCost);
        fr.querySelector('.quote-final-total').textContent = formatNumber(tQuote);
        fr.querySelector('.difference-cell').textContent = formatNumber(tQuote - tCost);
    }
    const mr = document.querySelector('.markup-row');
    if (mr && tQuote > 0) mr.querySelector('.margin-cell').textContent = (((tQuote - tCost) / tQuote) * 100).toFixed(1) + ' %';
}

/**
 * 을지 생성 모달 열기
 */
function openDetailedCreateModal() {
    const modal = document.getElementById('detailedCreateModal');
    if (modal) {
        modal.style.display = 'flex';
        // 제목과 작성자 자동 채우기
        document.getElementById('detailedTitle').value = priceCompareData?.title || '';
        document.getElementById('detailedCreator').value = priceCompareData?.creator || '';
        document.getElementById('detailedDescription').value = '';
    }
}

/**
 * 을지 생성 모달 닫기
 */
function closeDetailedCreateModal() {
    const modal = document.getElementById('detailedCreateModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * 모달에서 을지 생성
 */
async function createDetailedFromModal() {
    const title = document.getElementById('detailedTitle').value.trim();
    const creator = document.getElementById('detailedCreator').value.trim();
    const description = document.getElementById('detailedDescription').value.trim();

    // 필수 필드 검증
    if (!title) {
        alert('제목을 입력해주세요.');
        document.getElementById('detailedTitle').focus();
        return;
    }
    if (!creator) {
        alert('작성자를 입력해주세요.');
        document.getElementById('detailedCreator').focus();
        return;
    }

    if (!priceCompareData || !priceCompareData.folder_id) {
        alert('폴더 정보를 찾을 수 없습니다.');
        return;
    }

    if (!priceCompareId) {
        alert('내정가 비교서 ID를 찾을 수 없습니다.');
        return;
    }

    const requestData = {
        folder_id: priceCompareData.folder_id,
        price_compare_id: priceCompareId,
        title: title,
        creator: creator,
        description: description || null
    };

    try {
        const response = await fetch('/api/v1/quotation/detailed', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '을지 생성 실패');
        }

        const result = await response.json();
        alert('을지가 성공적으로 생성되었습니다.');
        closeDetailedCreateModal();

        // 생성된 을지 상세 페이지로 이동
        location.href = `/service/quotation/general/detailed/detail/${result.detailed_id}`;
    } catch (error) {
        console.error('을지 생성 오류:', error);
        alert('을지 생성 중 오류가 발생했습니다: ' + error.message);
    }
}

// 모달 외부 클릭 시 닫기
window.addEventListener('click', function(event) {
    const modal = document.getElementById('detailedCreateModal');
    if (event.target === modal) {
        closeDetailedCreateModal();
    }
});

function createDetailedFromCompare() { location.href = `/service/quotation/general/detailed/register?folder_id=${priceCompareData.folder_id}`; }
function createHeaderFromCompare() { location.href = `/service/quotation/general/header/register?folder_id=${priceCompareData.folder_id}`; }
function groupByMajorThenMachine(res) {
    const g = {}; res.forEach(i => {
        const maj = i.major || '기타', mach = i.machine_name || '미분류';
        if (!g[maj]) g[maj] = {}; if (!g[maj][mach]) g[maj][mach] = [];
        g[maj][mach].push(i);
    }); return g;
}
function formatNumber(n) { return (n || 0).toLocaleString('ko-KR'); }
function parseNumber(s) { return parseInt(s?.toString().replace(/[^0-9.-]/g, '')) || 0; }
function toggleEditMode(mode) { location.href = `?mode=${mode || 'edit'}`; }

/**
 * 내정가비교서 삭제
 */
async function deletePriceCompare() {
    if (!priceCompareId) {
        alert('삭제할 문서 ID를 찾을 수 없습니다.');
        return;
    }

    if (!confirm('이 내정가 견적 비교서를 삭제하시겠습니까?')) {
        return;
    }

    try {
        const response = await fetch(`/api/v1/quotation/price_compare/${priceCompareId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            alert('내정가 견적 비교서가 성공적으로 삭제되었습니다.');
            window.history.back(); // 목록으로 돌아가기
        } else {
            const error = await response.json();
            alert('삭제 실패: ' + (error.detail || '알 수 없는 오류'));
        }
    } catch (error) {
        console.error('Delete error:', error);
        alert('삭제 중 오류가 발생했습니다.');
    }
}