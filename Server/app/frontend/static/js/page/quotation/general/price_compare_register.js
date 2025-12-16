let machineList = [];
let selectedMachineIds = new Set();
let generalList = [];

document.addEventListener('DOMContentLoaded', () => {
    loadMachines();
    loadGenerals(); // 모달의 프로젝트 선택박스 채우기용
});

/**
 * 장비 견적서 목록 로드 (Machine API)
 */
async function loadMachines() {
    const loading = document.getElementById('loading');
    const container = document.getElementById('tableContainer');
    const searchVal = document.getElementById('searchInput').value;

    loading.style.display = 'block';
    container.innerHTML = '';

    try {
        // 검색어가 있으면 search 엔드포인트 사용, 없으면 목록 조회 사용
        // MACHINE API 참조
        let url = '/api/v1/quotation/machine?include_schema=true&limit=100';
        if (searchVal) {
            url = `/api/v1/quotation/machine/search?search=${encodeURIComponent(searchVal)}&include_schema=true`;
        }

        const res = await fetch(url);
        if (!res.ok) throw new Error('목록 로드 실패');
        
        const data = await res.json();
        machineList = data.items || [];
        
        renderTable(data.schema, machineList);
    } catch (err) {
        console.error(err);
        container.innerHTML = '<div class="empty-state">데이터를 불러오지 못했습니다.</div>';
    } finally {
        loading.style.display = 'none';
    }
}

/**
 * 테이블 렌더링
 */
function renderTable(schema, items) {
    const container = document.getElementById('tableContainer');
    
    if (!items || items.length === 0) {
        container.innerHTML = '<div class="empty-state">등록된 장비 견적서가 없습니다.</div>';
        return;
    }

    let html = `
        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th class="col-center" width="50">선택</th>
                        <th>장비명</th>
                        <th>작성자</th>
                        <th>비고</th>
                        <th class="col-center" width="150">최종수정일</th>
                    </tr>
                </thead>
                <tbody>
    `;

    items.forEach(item => {
        const isChecked = selectedMachineIds.has(item.id) ? 'checked' : '';
        const updated = item.updated_at ? new Date(item.updated_at).toLocaleString() : '-';
        
        html += `
            <tr class="clickable" onclick="toggleSelection('${item.id}')">
                <td class="col-center" onclick="event.stopPropagation()">
                    <input type="checkbox" class="machine-checkbox" value="${item.id}" ${isChecked} onchange="toggleSelection('${item.id}')">
                </td>
                <td class="font-bold">${item.name}</td>
                <td>${item.creator}</td>
                <td class="text-gray-500">${item.description || '-'}</td>
                <td class="col-center text-gray-500">${updated}</td>
            </tr>
        `;
    });

    html += '</tbody></table></div>';
    container.innerHTML = html;
    updateActionButtons();
}

/**
 * 선택 토글 로직
 */
function toggleSelection(id) {
    if (selectedMachineIds.has(id)) {
        selectedMachineIds.delete(id);
    } else {
        selectedMachineIds.add(id);
    }
    
    // UI 업데이트
    const checkbox = document.querySelector(`.machine-checkbox[value="${id}"]`);
    if (checkbox) checkbox.checked = selectedMachineIds.has(id);
    
    updateActionButtons();
}

function updateActionButtons() {
    const count = selectedMachineIds.size;
    document.getElementById('selectedCount').textContent = count;
    document.getElementById('createBtn').disabled = (count === 0);
}

/**
 * 프로젝트(General) 목록 로드 (General API)
 * Price Compare 생성 시 general_id가 필수이므로 필요함
 */
async function loadGenerals() {
    const select = document.getElementById('regGeneralId');
    try {
        // GENERAL API 참조
        const res = await fetch('/api/v1/quotation/general?limit=100');
        if (res.ok) {
            const data = await res.json();
            const items = data.items || [];
            
            items.forEach(g => {
                const opt = document.createElement('option');
                opt.value = g.id;
                opt.textContent = g.name;
                select.appendChild(opt);
            });
        }
    } catch (e) {
        console.error('General load fail:', e);
    }
}

/**
 * 모달 열기
 */
function openCreateModal() {
    if (selectedMachineIds.size === 0) return alert('선택된 장비가 없습니다.');
    
    const modal = document.getElementById('createModal');
    const list = document.getElementById('modalSelectedList');
    
    // 선택된 장비 목록 표시
    list.innerHTML = '';
    let count = 0;
    machineList.forEach(m => {
        if (selectedMachineIds.has(m.id)) {
            const li = document.createElement('li');
            li.innerHTML = `<span>${m.name}</span> <small>${m.creator}</small>`;
            list.appendChild(li);
            count++;
        }
    });
    
    document.getElementById('modalSelectedCount').textContent = count;
    modal.style.display = 'flex';
}

function closeCreateModal() {
    document.getElementById('createModal').style.display = 'none';
}

/**
 * 내정가 견적비교서 생성 요청 (Price Compare API)
 */
async function submitPriceCompare() {
    const generalId = document.getElementById('regGeneralId').value;
    const creator = document.getElementById('regCreator').value;
    const description = document.getElementById('regDescription').value;
    
    if (!generalId) return alert('프로젝트(General)를 선택해주세요.');
    if (!creator) return alert('작성자를 입력해주세요.');
    if (selectedMachineIds.size === 0) return alert('선택된 장비가 없습니다.');

    // PRICE_COMPARE API 참조
    const payload = {
        general_id: generalId,
        creator: creator,
        description: description,
        machine_ids: Array.from(selectedMachineIds) // 필수 배열 필드
    };

    const btn = document.querySelector('#createModal .btn-primary');
    btn.disabled = true;
    btn.textContent = '생성 중...';

    try {
        const res = await fetch('/api/v1/quotation/price_compare', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            const data = await res.json();
            alert('내정가 견적 비교서가 생성되었습니다.');
            // 생성된 상세 페이지로 이동하거나 목록을 새로고침
            window.location.href = `/service/quotation/price_compare/${data.id}`;
        } else {
            const err = await res.json();
            alert('생성 실패: ' + (err.detail || '알 수 없는 오류'));
        }
    } catch (e) {
        console.error(e);
        alert('요청 중 오류가 발생했습니다.');
    } finally {
        btn.disabled = false;
        btn.textContent = '생성 완료';
    }
}

function handleSearch(e) {
    if (e.key === 'Enter') loadMachines();
}