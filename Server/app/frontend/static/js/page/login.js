// login.js
//
// 로그인 페이지(login.html)의 클라이언트 측 JavaScript 로직을 정의합니다.
// - 폼 제출 시 API를 호출하여 로그인 처리 및 결과에 따른 페이지 이동을 수행합니다.
//

document.getElementById('loginForm').addEventListener('submit', async function(e) {
    // 폼 기본 제출 동작(페이지 새로고침)을 방지합니다.
    e.preventDefault();
    
    // 폼에서 아이디와 비밀번호 값을 가져옵니다.
    const formData = {
        id: document.getElementById('id').value,
        pwd: document.getElementById('pwd').value // 비밀번호는 이 단계에서 해싱되지 않고 전송될 수 있으므로, 보안에 주의해야 합니다. (백엔드에서 해싱 필수)
    };
    
    try {
        // TODO: 실제 로그인 API 구현 필요
        // 현재는 서버의 '/api/v1/account/check' API를 임시로 사용하여 아이디 존재 여부만 확인합니다.
        
        // --- 임시 계정 확인 API 호출 ---
        // 로그인 시도 시, 먼저 해당 아이디가 시스템에 등록되어 있는지 확인하는 API를 호출합니다.
        const checkResponse = await fetch('/api/v1/account/check', {
            method: 'POST', // POST 요청
            headers: {
                'Content-Type': 'application/json', // JSON 형식으로 데이터 전송
            },
            body: JSON.stringify({ id: formData.id }) // 아이디만 포함하여 요청
        });
        
        const checkData = await checkResponse.json(); // 응답을 JSON으로 파싱
        
        // 아이디가 사용 가능(available) 상태이면, 등록되지 않은 아이디로 간주합니다.
        if (checkData.available) {
            alert('등록되지 않은 아이디입니다.');
            return; // 함수 실행 중단
        }
        
        // --- 로그인 성공 처리 (임시 로직) ---
        // 실제 비밀번호 검증은 백엔드에서 수행되어야 하지만, 여기서는 아이디가 존재하면 로그인 성공으로 간주하는 임시 로직입니다.
        // 사용자 정보를 로컬 스토리지에 저장합니다. (세션 관리에 사용될 수 있음)
        localStorage.setItem('user', JSON.stringify({
            id: formData.id,
            loginTime: new Date().toISOString() // 로그인 시간 기록
        }));
        
        alert('로그인 되었습니다.');
        // 로그인 성공 후 견적서 목록 페이지로 이동합니다.
        window.location.href = '/service/quotation/machine';
        
    } catch (error) {
        console.error('Error:', error); // 에러 발생 시 콘솔에 기록
        alert('로그인 중 오류가 발생했습니다.'); // 사용자에게 에러 메시지 표시
    }
});