/**
 * 견적서(갑지) 생성 - 을지 선택 및 요약 데이터 매칭
 */
let selectedDetailedId = null;
const currentFolderId = document.getElementById('hiddenFolderId').value;
let generalCreator = ''; // General의 작성자 저장
let generalClient = ''; // General의 고객사명 저장
let folderTitle = ''; // Folder 제목 저장

document.addEventListener('DOMContentLoaded', async () => {
    await loadGeneralInfo();
    await loadDetailedQuotations();
});

async function loadGeneralInfo() {
    try {
        // Folder 정보 가져오기
        const folderRes = await fetch(`/api/v1/quotation/folder/${currentFolderId}`);
        if (folderRes.ok) {
            const folderData = await folderRes.json();
            folderTitle = folderData.title || '알 수 없음';

            const nameEl = document.getElementById('displayGeneralName');
            if (nameEl) nameEl.textContent = folderTitle;

            // General 정보 가져오기 (작성자 및 고객사명 획득)
            if (folderData.general_id) {
                const generalRes = await fetch(`/api/v1/quotation/general/${folderData.general_id}`);
                if (generalRes.ok) {
                    const generalData = await generalRes.json();
                    generalCreator = generalData.creator || '';
                    generalClient = generalData.client || '';
                }
            }
        }
    } catch (e) {
        console.error('Folder Info Load Error:', e);
        const nameEl = document.getElementById('displayGeneralName');
        if (nameEl) nameEl.textContent = '정보 로드 실패';
    }
}

async function loadDetailedQuotations() {
    const container = document.getElementById('tableContainer');
    const loading = document.getElementById('loading');
    if (loading) loading.style.display = 'block';

    try {
        const res = await fetch(`/api/v1/quotation/folder/${currentFolderId}?include_resources=true`);
        const data = await res.json();
        // API 응답의 resources 배열에서 detailed 추출
        const resources = data.resources || [];
        const allItems = resources.filter(r => r.table_name === '견적서(을지)');
        const items = allItems;

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

    // 기본값 채우기: 제목, 고객사명, 작성자
    document.getElementById('regTitle').value = folderTitle ? `${folderTitle} - 견적서 (갑지)` : '견적서 (갑지)';
    document.getElementById('regClient').value = generalClient;
    document.getElementById('regCreator').value = generalCreator;

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
        folder_id: currentFolderId,
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
            // folder에서 general_id를 가져와서 리다이렉트
            const folderRes = await fetch(`/api/v1/quotation/folder/${currentFolderId}`);
            if (folderRes.ok) {
                const folderData = await folderRes.json();
                window.location.href = `/service/quotation/general/form?mode=view&id=${folderData.general_id}`;
            }
        } else {
            const err = await res.json();
            alert('생성 실패: ' + (err.detail || '오류 발생'));
        }
    } catch (e) { console.error("서버 전송 중 오류:", e); }
}