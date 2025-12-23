/**
 * 견적서(갑지) 생성 - 을지 선택 및 요약 데이터 매칭
 */
let selectedDetailedId = null;
const currentGeneralId = document.getElementById('hiddenGeneralId').value;

document.addEventListener('DOMContentLoaded', async () => {
    await loadGeneralInfo();
    await loadDetailedQuotations();
});

async function loadGeneralInfo() {
    try {
        const res = await fetch(`/api/v1/quotation/general/${currentGeneralId}`);
        if (res.ok) {
            const data = await res.json();
            const info = data.general || data;
            
            // [안전장치] 요소가 존재할 때만 텍스트 및 값 설정
            const nameEl = document.getElementById('displayGeneralName');
            if (nameEl) nameEl.textContent = info.name;
            
            const clientEl = document.getElementById('regClient');
            if (clientEl) clientEl.value = info.client || '';
            
            const creatorEl = document.getElementById('regCreator');
            if (creatorEl) creatorEl.value = info.creator || '';
        }
    } catch (e) { console.error("프로젝트 정보 로드 중 오류:", e); }
}

async function loadDetailedQuotations() {
    const container = document.getElementById('tableContainer');
    const loading = document.getElementById('loading');
    if (loading) loading.style.display = 'block';

    try {
        const res = await fetch(`/api/v1/quotation/general/${currentGeneralId}?include_relations=true`);
        const data = await res.json();
        const allItems = data.related_documents || [];
        const items = allItems.filter(item => (item.category || "").includes("을지"));

        if (items.length === 0) {
            container.innerHTML = '<div class="empty-state">선택할 수 있는 상세 견적서(을지)가 없습니다.</div>';
            return;
        }

        let html = `<div class="table-container"><table class="data-table">
            <thead><tr><th width="50" class="col-center">선택</th><th>제목</th><th>작성자</th><th class="col-center">최종수정일</th></tr></thead>
            <tbody>`;

        items.forEach(item => {
            html += `<tr class="clickable" onclick="selectDetailed('${item.id}')">
                <td class="col-center"><input type="radio" name="detailed-select" value="${item.id}"></td>
                <td class="font-bold">${item.title}</td><td>${item.creator}</td>
                <td class="col-center">${item.updated_at.substring(0, 10)}</td></tr>`;
        });
        container.innerHTML = html + '</tbody></table></div>';
    } catch (e) { container.innerHTML = '목록 로드 실패'; }
    finally { if (loading) loading.style.display = 'none'; }
}

function selectDetailed(id) {
    selectedDetailedId = id;
    const radio = document.querySelector(`input[name="detailed-select"][value="${id}"]`);
    if (radio) radio.checked = true;
    
    const createBtn = document.getElementById('createBtn');
    if (createBtn) {
        createBtn.disabled = false;
    }
}

function openCreateModal() {
    if (!selectedDetailedId) {
        alert('요약할 을지(상세 견적서)를 먼저 선택해주세요.');
        return;
    }
    
    const modal = document.getElementById('createModal');
    if (modal) {
        modal.style.display = 'flex';
    } else {
        console.error("ID가 'createModal'인 요소를 찾을 수 없습니다.");
    }
}

function closeCreateModal() {
    const modal = document.getElementById('createModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

async function submitHeader() {
    const title = document.getElementById('regTitle').value.trim();
    const client = document.getElementById('regClient').value.trim();
    const picName = document.getElementById('regPicName').value.trim();
    const picPosition = document.getElementById('regPicPosition').value.trim();
    const creator = document.getElementById('regCreator').value.trim();

    if (!title || !client || !picName || !picPosition || !creator) {
        alert('모든 필수 정보를 입력해주세요.');
        return;
    }

    const payload = {
        general_id: currentGeneralId,
        detailed_id: selectedDetailedId,
        title: title,
        client: client,
        pic_name: picName,
        pic_position: picPosition,
        creator: creator
    };

    try {
        const res = await fetch('/api/v1/quotation/header', {
            method: 'POST', 
            headers: { 'Content-Type': 'application/json' }, 
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            alert('갑지가 생성되었습니다.');
            window.location.href = `/service/quotation/general/form?mode=view&id=${currentGeneralId}`;
        } else {
            const err = await res.json();
            alert('생성 실패: ' + (err.detail || '오류 발생'));
        }
    } catch (e) { console.error("서버 전송 중 오류:", e); }
}