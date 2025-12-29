let selectedPriceCompareId = null;
const currentFolderId = document.getElementById('hiddenFolderId').value;
let generalCreator = ''; // General의 작성자 저장
let folderTitle = ''; // Folder 제목 저장

document.addEventListener('DOMContentLoaded', async () => {
    await loadGeneralInfo();
    await loadPriceCompares();
});

async function loadGeneralInfo() {
    try {
        // Folder 정보 가져오기
        const folderRes = await fetch(`/api/v1/quotation/folder/${currentFolderId}`);
        if (folderRes.ok) {
            const folderData = await folderRes.json();
            folderTitle = folderData.title || '알 수 없음';
            document.getElementById('displayGeneralName').textContent = folderTitle;

            // General 정보 가져오기 (작성자 획득)
            if (folderData.general_id) {
                const generalRes = await fetch(`/api/v1/quotation/general/${folderData.general_id}`);
                if (generalRes.ok) {
                    const generalData = await generalRes.json();
                    generalCreator = generalData.creator || '';
                }
            }
        }
    } catch (e) {
        console.error('Folder Info Load Error:', e);
        document.getElementById('displayGeneralName').textContent = '정보 로드 실패';
    }
}

/**
 * 내정가 비교서 목록 로드 및 필터링 강화
 */
async function loadPriceCompares() {
    const container = document.getElementById('tableContainer');
    const loading = document.getElementById('loading');
    
    loading.style.display = 'block';
    container.innerHTML = '';

    try {
        const res = await fetch(`/api/v1/quotation/folder/${currentFolderId}?include_resources=true`);
        if (!res.ok) throw new Error('연관 목록 로드 실패');

        const data = await res.json();
        // API 응답의 resources 배열에서 price_compare 추출
        const resources = data.resources || [];
        const allItems = resources.filter(r => r.table_name === '내정가 비교');

        console.log("받은 데이터:", allItems);

        // folder의 price_compare를 items로 사용
        const items = allItems;

        if (items.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    선택할 수 있는 내정가 비교서가 없습니다. <br>
                    (응답 데이터 수: ${allItems.length}개)
                </div>`;
            return;
        }

        let html = `
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th width="50" class="col-center">선택</th>
                            <th>비교표 제목</th>
                            <th>작성자</th>
                            <th class="col-center">최종수정일</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        items.forEach(item => {
            // 날짜 포맷팅 (YYYY-MM-DD HH:mm)
            const dateStr = item.updated_at ? item.updated_at.replace('T', ' ').substring(0, 16) : '-';
            
            html += `
                <tr class="clickable" onclick="selectCompare('${item.id}')">
                    <td class="col-center">
                        <input type="radio" name="compare-select" value="${item.id}" 
                            ${selectedPriceCompareId === item.id ? 'checked' : ''} 
                            onclick="event.stopPropagation()">
                    </td>
                    <td class="font-bold">${item.title || '제목 없음'}</td>
                    <td>${item.creator || '-'}</td>
                    <td class="col-center text-gray-500">${dateStr}</td>
                </tr>
            `;
        });

        html += '</tbody></table></div>';
        container.innerHTML = html;

    } catch (e) {
        console.error('목록 로드 중 에러:', e);
        container.innerHTML = '<div class="empty-state">목록을 불러오는 중 오류가 발생했습니다.</div>';
    } finally {
        loading.style.display = 'none';
    }
}

function selectCompare(id) {
    selectedPriceCompareId = id;
    const radio = document.querySelector(`input[name="compare-select"][value="${id}"]`);
    if (radio) radio.checked = true;
    
    // 버튼 활성화
    const createBtn = document.getElementById('createBtn');
    if (createBtn) createBtn.disabled = false;
}

function openCreateModal() {
    if (!selectedPriceCompareId) return alert('내정가 비교서를 선택해주세요.');

    // 기본값 채우기: 제목과 작성자
    document.getElementById('regTitle').value = folderTitle ? `${folderTitle} - 상세 견적서 (을지)` : '상세 견적서 (을지)';
    document.getElementById('regCreator').value = generalCreator;

    document.getElementById('createModal').style.display = 'flex';
}

function closeCreateModal() {
    document.getElementById('createModal').style.display = 'none';
}

/**
 * 을지 생성 요청
 */
async function submitDetailed() {
    const title = document.getElementById('regTitle').value.trim();
    const creator = document.getElementById('regCreator').value.trim();
    const description = document.getElementById('regDescription').value.trim();
    
    if (!title || !creator) return alert('제목과 작성자를 입력해주세요.');

    const payload = {
        folder_id: currentFolderId,
        price_compare_id: selectedPriceCompareId,
        title: title,
        creator: creator,
        description: description
    };

    const submitBtn = document.querySelector('#createModal .btn-primary');
    submitBtn.disabled = true;
    submitBtn.textContent = '생성 중...';

    try {
        const res = await fetch('/api/v1/quotation/detailed', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            const result = await res.json();
            alert('상세 견적서(을지)가 생성되었습니다.');
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
    } catch (e) {
        console.error(e);
        alert('서버 통신 중 오류가 발생했습니다.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = '을지 생성 완료';
    }
}