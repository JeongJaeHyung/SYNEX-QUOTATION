let selectedPriceCompareId = null;
const currentGeneralId = document.getElementById('hiddenGeneralId').value;

document.addEventListener('DOMContentLoaded', async () => {
    await loadGeneralInfo();
    await loadPriceCompares(); 
});

async function loadGeneralInfo() {
    try {
        const res = await fetch(`/api/v1/quotation/general/${currentGeneralId}`);
        if (res.ok) {
            const data = await res.json();
            const info = data.general || data;
            document.getElementById('displayGeneralName').textContent = info.name;
            document.getElementById('regCreator').value = info.creator || '';
        }
    } catch (e) { console.error('프로젝트 정보 로드 에러:', e); }
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
        const res = await fetch(`/api/v1/quotation/general/${currentGeneralId}?include_relations=true`);
        if (!res.ok) throw new Error('연관 목록 로드 실패');
        
        const data = await res.json();
        // API 응답의 related_documents에서 데이터 추출
        const allItems = data.related_documents || [];
        
        console.log("받은 데이터:", allItems);

        // [수정 포인트] category 명칭에 '비교견적서' 또는 '내정가'가 포함되면 필터링 통과
        const items = allItems.filter(item => {
            const category = item.category || "";
            const tableName = item.table_name || "";
            
            return category.includes("비교견적서") || 
                   category.includes("내정가") || 
                   tableName === "PriceCompare";
        });

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
        general_id: currentGeneralId,
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
            alert('상세 견적서(을지)가 생성되었습니다.');
            window.location.href = `/service/quotation/general/form?mode=view&id=${currentGeneralId}`;
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