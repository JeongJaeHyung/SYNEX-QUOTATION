/**
 * 견적서 갑지 - 특정 컬럼 수정 방지 및 UI 통합 버전
 */
let headerId = null;
let headerData = null;
let pageMode = 'view';

document.addEventListener('DOMContentLoaded', () => {
    const pathParts = window.location.pathname.split('/').filter(p => p !== '');
    headerId = pathParts[pathParts.length - 1];
    
    if (headerId && headerId !== 'detail') {
        loadHeaderData(headerId);
    }
    setupEventListeners();
});

// 데이터 로드
async function loadHeaderData(id) {
    const loading = document.getElementById('loading');
    const container = document.getElementById('summaryContainer');

    try {
        const response = await fetch(`/api/v1/quotation/header/${id}`);
        if (!response.ok) throw new Error('로드 실패');
        
        headerData = await response.json();
        renderHeaderPage(headerData);
        toggleEditMode('view');
        
        if (loading) loading.style.display = 'none';
        if (container) container.style.display = 'block';
    } catch (error) {
        if (loading) loading.innerHTML = '<p style="color: red;">데이터 로딩 실패</p>';
    }
}

function renderHeaderPage(data) {
    const updateDate = data.updated_at ? new Date(data.updated_at) : new Date();
    document.getElementById('quotationDate').textContent = formatDate(updateDate);
    document.getElementById('senderCompany').textContent = data.client || '';

    // 담당자 매핑
    const picName = data.pic_name || '';
    const picPos = data.pic_position || '';
    document.getElementById('picInfoLabel').textContent = `${picName} ${picPos}님 귀하`.trim();

    // 제목 연동 초기화
    const docTitle = data.title || '';
    document.getElementById('quotationTitle').textContent = docTitle;
    document.getElementById('documentTitle').textContent = docTitle;

    // 견적금액 & Best Nego Total 통합 (초기값 0 또는 서버값)
    const initialPrice = data.price || 0;
    document.getElementById('negoTotal').textContent = formatNumber(initialPrice);
    document.getElementById('totalAmountVat').textContent = formatNumber(initialPrice);
    document.getElementById('quotationAmountText').textContent = numberToKorean(initialPrice);

    // 비고란
    document.getElementById('remarksSpecial').innerText = (data.description_1 || '').trim();
    document.getElementById('remarksGeneral').innerText = (data.description_2 || '').trim();

    // 공급자 정보 고정 (사장님 성함)
    document.getElementById('supplierName').value = "정현우";

    renderTableWithMerge(data.header_resources || []);
    updateTableTotalOnly(); 
}

/**
 * 장비명 기준 셀 병합 렌더링
 */
function renderTableWithMerge(resources) {
    const tbody = document.getElementById('quotationTableBody');
    tbody.innerHTML = '';

    const machineCounts = {};
    resources.forEach(item => {
        const m = item.machine || '기타';
        machineCounts[m] = (machineCounts[m] || 0) + 1;
    });

    const renderedMachines = new Set();

    resources.forEach((item, index) => {
        const row = document.createElement('tr');
        const machineName = item.machine || '기타';
        
        let machineCellHtml = '';
        if (!renderedMachines.has(machineName)) {
            const count = machineCounts[machineName];
            machineCellHtml = `<td class="col-machine col-center" rowspan="${count}">${machineName}</td>`;
            renderedMachines.add(machineName);
        }

        row.innerHTML = `
            <td class="col-no">${index + 1}</td>
            ${machineCellHtml}
            <td class="col-name">${item.name || ''}</td>
            <td class="col-spec">${item.spac || ''}</td>
            <td class="col-quantity col-center">${item.compare || 0}</td>
            <td class="col-unit col-center">${item.unit || ''}</td>
            <td class="col-price col-right">${formatNumber(item.solo_price)}</td>
            <td class="col-unit-price col-right">${formatNumber(item.subtotal)}</td>
            <td class="col-remarks col-left">${item.description || ''}</td>
        `;
        tbody.appendChild(row);
    });
}

// 모드 전환 및 우측 메뉴 제어
function toggleEditMode(mode) {
    pageMode = mode;
    const container = document.getElementById('summaryContainer');
    const editBtn = document.getElementById('btnToggleEdit');

    container.classList.toggle('edit-mode', mode === 'edit');
    
    if (editBtn) {
        editBtn.textContent = (mode === 'edit') ? '저장하기' : '수정하기';
        editBtn.className = (mode === 'edit') ? 'btn btn-success' : 'btn btn-primary';
        editBtn.onclick = (mode === 'edit') ? saveSummary : () => toggleEditMode('edit');
    }

    // [수정] 특정 컬럼 보호 로직
    // 수정 가능한 요소들: 제목, 비고란, 규격, 수량, 단위, 단가, 비고(테이블), Nego금액
    const editables = document.querySelectorAll(
        '.editable-text, ' +
        '#quotationTableBody td.col-spec, ' +
        '#quotationTableBody td.col-quantity, ' +
        '#quotationTableBody td.col-unit, ' +
        '#quotationTableBody td.col-price, ' +
        '#quotationTableBody td.col-remarks, ' +
        '#negoTotal'
    );
    
    editables.forEach(el => el.contentEditable = (mode === 'edit'));

    if (mode === 'view' && headerData) renderHeaderPage(headerData);
}

function setupEventListeners() {
    const container = document.getElementById('summaryContainer');
    
    container.addEventListener('input', (e) => {
        if (pageMode !== 'edit') return;
        const target = e.target;

        // 제목 실시간 연동
        if (target.id === 'quotationTitle') {
            document.getElementById('documentTitle').textContent = target.textContent;
        }

        // 테이블 계산 (수량/단가 수정 시 공급가액 자동 계산)
        if (target.classList.contains('col-quantity') || target.classList.contains('col-price')) {
            const row = target.parentElement;
            const qty = parseNumber(row.querySelector('.col-quantity').textContent);
            const price = parseNumber(row.querySelector('.col-price').textContent);
            row.querySelector('.col-unit-price').textContent = formatNumber(qty * price);
            updateTableTotalOnly();
        }

        // Best Nego Total 수정 시 상단 견적금액 동기화
        if (target.id === 'negoTotal') {
            const negoVal = parseNumber(target.textContent);
            document.getElementById('totalAmountVat').textContent = formatNumber(negoVal);
            document.getElementById('quotationAmountText').textContent = numberToKorean(negoVal);
        }
    });

    // 엔터 키 이동
    container.addEventListener('keydown', (e) => {
        if (pageMode === 'edit' && e.key === 'Enter') {
            e.preventDefault();
            const editables = Array.from(document.querySelectorAll('[contenteditable="true"]'));
            const idx = editables.indexOf(document.activeElement);
            if (idx > -1 && idx < editables.length - 1) editables[idx + 1].focus();
        }
    });

    // 포커스 아웃 시 콤마 처리
    container.addEventListener('blur', (e) => {
        if (e.target.classList.contains('col-price') || e.target.id === 'negoTotal') {
            const val = parseNumber(e.target.textContent);
            e.target.textContent = formatNumber(val);
        }
    }, true);
}

function updateTableTotalOnly() {
    const rows = document.querySelectorAll('#quotationTableBody tr');
    let tableSum = 0;
    let qtySum = 0;
    rows.forEach(row => {
        const subCell = row.querySelector('.col-unit-price');
        const qtyCell = row.querySelector('.col-quantity');
        if (subCell && qtyCell) {
            tableSum += parseNumber(subCell.textContent);
            qtySum += parseNumber(qtyCell.textContent);
        }
    });
    document.getElementById('totalQtySum').textContent = qtySum;
    document.getElementById('summaryAmount').textContent = formatNumber(tableSum);
    document.getElementById('totalAmount').textContent = formatNumber(tableSum);
}

// 저장 로직
async function saveSummary() {
    if (!headerId || !headerData) return;
    try {
        let currentMachine = "";
        const resources = Array.from(document.querySelectorAll('#quotationTableBody tr')).map((row) => {
            const machineCell = row.querySelector('.col-machine');
            if (machineCell) currentMachine = machineCell.textContent.trim();
            return {
                machine: currentMachine,
                name: row.querySelector('.col-name').textContent.trim(),
                spac: row.querySelector('.col-spec').textContent.trim(),
                compare: parseNumber(row.querySelector('.col-quantity').textContent),
                unit: row.querySelector('.col-unit').textContent.trim(),
                solo_price: parseNumber(row.querySelector('.col-price').textContent),
                subtotal: parseNumber(row.querySelector('.col-unit-price').textContent),
                description: row.querySelector('.col-remarks').textContent.trim()
            };
        });

        const payload = {
            title: document.getElementById('quotationTitle').textContent.trim(),
            client: document.getElementById('senderCompany').textContent.trim(),
            price: parseNumber(document.getElementById('negoTotal').textContent),
            creator: headerData.creator,
            pic_name: headerData.pic_name,
            pic_position: headerData.pic_position,
            description_1: document.getElementById('remarksSpecial').innerText.trim(),
            description_2: document.getElementById('remarksGeneral').innerText.trim(),
            header_resources: resources
        };

        const res = await fetch(`/api/v1/quotation/header/${headerId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            alert('저장되었습니다.');
            headerData = await res.json();
            toggleEditMode('view');
        }
    } catch (e) { alert('통신 오류'); }
}

// 유틸리티
function formatNumber(n) { return (n || 0).toLocaleString('ko-KR'); }
function parseNumber(s) { return parseInt(s.toString().replace(/[^0-9]/g, '')) || 0; }
function formatDate(d) { return `${d.getFullYear()}년 ${d.getMonth() + 1}월 ${d.getDate()}일`; }
function numberToKorean(n) {
    if (n === 0) return '일금 영원 정';
    const units = ['', '만', '억', '조'];
    const nums = ['', '일', '이', '삼', '사', '오', '육', '칠', '팔', '구'];
    const pos = ['', '십', '백', '천'];
    let res = '', s = n.toString();
    for (let i = 0; i < s.length; i++) {
        let d = parseInt(s[s.length - 1 - i]);
        if (d !== 0) res = nums[d] + pos[i % 4] + res;
        if (i % 4 === 3 || i === s.length - 1) {
            const u = units[Math.floor(i / 4)];
            if (res.match(/[일이삼사오육칠팔구]/) && !res.includes(u)) res = u + res;
        }
    }
    return '일금 ' + res.replace(/^일십/, '십') + '원 정';
}
function exportPDF() { window.print(); }
function goBack() { window.history.back(); }