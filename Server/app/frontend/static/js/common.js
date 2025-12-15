// static/js/common.js

// [보안] 페이지 로드 시 즉시 실행
(function() {
    const token = localStorage.getItem('access_token');
    const currentPath = window.location.pathname;

    // 1. 로그인/회원가입 페이지는 검사 제외
    const publicPages = ['/login', '/register', '/'];
    if (publicPages.includes(currentPath)) {
        // 이미 로그인했는데 로그인 페이지로 오면 메인으로 보냄
        if (token && currentPath === '/login') {
            window.location.href = '/service/quotation/machine';
        }
        return;
    }

    // 2. 토큰이 없으면 로그인 페이지로 강제 이동 (Kick out)
    if (!token) {
        alert('로그인이 필요한 서비스입니다.');
        window.location.href = '/login';
        return; // 이후 로직 실행 차단
    }

    // 3. (선택) 토큰이 있는데 만료되었는지 체크하는 로직은 
    //    API 호출 시 401 에러가 나면 authFetch에서 처리함.
})();

// ... (기존 authFetch 함수 등) ...