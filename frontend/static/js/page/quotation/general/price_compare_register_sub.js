// price_compare_register_sub.js

let machineList = [];
let selectedMachineIds = new Set();

// HTML의 히든 필드에서 General ID 가져오기
const currentGeneralId = document.getElementById('hiddenGeneralId').value;

document.addEventListener('DOMContentLoaded', async () => {
    // 1. 현재 General 프로젝트 이름 조회
    await loadGeneralInfo();
    // 2. 선택할 장비 목록 조회
    await loadMachines();
});

/**
 * General 정보 로드 (이름 표시용)
 */
async function loadGeneralInfo() {
    try {
        const res = await fetch(`/api/v1/quotation/general/${currentGeneralId}`);
        if (res.ok) {
            const data = await res.json();
            // API 응답 구조 유연하게 처리
            const name = data.name || (data.general ? data.general.name : '알 수 없음');
            document.getElementById('displayGeneralName').textContent = name;
            
            // 작성자 자동 채우기
            if (data.creator) {
                document.getElementById('regCreator').value = data.creator;
            }
        }
    } catch (e) {
        console.error('General Info Load Error:', e);
        document.getElementById('displayGeneralName').textContent = '정보 로드 실패';
    }
}

/**
 * 장비 목록 로드 (Machine API)
 */
async function loadMachines() {
    const loading = document.getElementById('loading');
    const container = document.getElementById('tableContainer');
    const searchVal = document.getElementById('searchInput').value;

    loading.style.display = 'block';
    container.innerHTML = '';

    try {
        // 검색어가 있으면 search 엔드포인트, 없으면 전체 목록 조회
        let url = '/api/v1/quotation/machine?include_schema=true&limit=100';
        if (searchVal) {
            url = `/api/v1/quotation/machine/search?search=${encodeURIComponent(searchVal)}&include_schema=true`;
        }

        const res = await fetch(url);
        if (!res.ok) throw new Error('장비 목록 로드 실패');

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
        container.innerHTML = '<div class="empty-state">선택 가능한 장비 견적서가 없습니다.</div>';
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
        const updated = item.updated_at ? new Date(item.updated_at).toLocaleDateString() : '-';
        
        // 행 클릭 시 선택 토글
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
    
    // 체크박스 UI 동기화
    const checkbox = document.querySelector(`.machine-checkbox[value="${id}"]`);
    if (checkbox) checkbox.checked = selectedMachineIds.has(id);
    
    updateActionButtons();
}

// 버튼 활성화/비활성화 업데이트
function updateActionButtons() {
    const count = selectedMachineIds.size;
    document.getElementById('selectedCount').textContent = count;
    document.getElementById('createBtn').disabled = (count === 0);
}

/**
 * 모달 열기
 */
function openCreateModal() {
    if (selectedMachineIds.size === 0) return alert('선택된 장비가 없습니다.');
    
    const modal = document.getElementById('createModal');
    const list = document.getElementById('modalSelectedList');
    
    // 선택된 장비 목록을 모달에 표시
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
 * [핵심] 내정가 견적비교서 생성 요청 (API 호출)
 */
async function submitPriceCompare() {
    const creator = document.getElementById('regCreator').value;
    const description = document.getElementById('regDescription').value;
    
    if (!creator) return alert('작성자를 입력해주세요.');
    
    const payload = {
        general_id: currentGeneralId,        // 고정된 General ID 사용
        creator: creator,
        description: description,
        machine_ids: Array.from(selectedMachineIds) // 선택된 장비 ID 목록
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
            alert('내정가 견적 비교서가 성공적으로 생성되었습니다.');
            
            // 성공 시, 다시 General 조회 화면으로 돌아갑니다.
            goBackToGeneral();
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

/**
 * 뒤로가기 (General 조회 화면으로 이동)
 */
function goBackToGeneral() {
    window.location.href = `/service/quotation/general/form?mode=view&id=${currentGeneralId}`;
}

// 엔터키 검색 지원
function handleSearch(e) {
    if (e.key === 'Enter') loadMachines();
}