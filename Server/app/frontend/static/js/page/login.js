
document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const idInput = document.getElementById('id');
    const pwdInput = document.getElementById('pwd');
    const submitBtn = document.querySelector('button[type="submit"]');
    
    // 1. 입력값 유효성 검사
    if (!idInput.value || !pwdInput.value) {
        alert('아이디와 비밀번호를 입력해주세요.');
        return;
    }

    const loginData = {
        id: idInput.value,
        pwd: pwdInput.value
    };
    
    try {
        // UI 피드백 (버튼 비활성화)
        submitBtn.disabled = true;
        submitBtn.textContent = '로그인 중...';

        // 2. 실제 Auth API 호출
        const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(loginData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // 3. [핵심] JWT 토큰 및 사용자 정보 저장
            // 나중에 API 호출 시 Authorization 헤더에 사용됨
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('user_role', data.role);
            localStorage.setItem('user_name', data.user_name);
            
            // 4. 메인 대시보드로 이동
            // alert(`${data.user_name}님 환영합니다!`); // (선택사항)
            window.location.href = '/service/quotation/machine';
        } else {
            // 5. 실패 처리 (401 Unauthorized 등)
            console.error('Login Failed:', data);
            alert(data.detail || '아이디 또는 비밀번호가 일치하지 않습니다.');
        }
        
    } catch (error) {
        console.error('Network Error:', error);
        alert('서버와 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
    } finally {
        // 버튼 상태 복구
        submitBtn.disabled = false;
        submitBtn.textContent = '로그인';
    }
});