// static/js/common.js 맨 상단

// [보안] 페이지 로드 시 즉시 실행 (이게 진짜 접근 통제입니다!)
(function() {
    const token = localStorage.getItem('access_token'); // 1. 토큰 확인
    const currentPath = window.location.pathname;

    // 예외 페이지 (로그인, 회원가입)
    const publicPages = ['/login', '/register', '/'];
    if (publicPages.includes(currentPath)) {
        return;
    }

    // 2. 토큰 없으면 로그인 페이지로 강제 추방 (Kick out)
    if (!token) {
        alert('로그인이 필요한 서비스입니다.');
        window.location.href = '/login';
        // 여기서 스크립트 실행을 멈춰야 함 (하지만 JS 특성상 HTML은 잠깐 보일 수 있음)
    }
})();

document.addEventListener('DOMContentLoaded', () => {
  highlightActiveNav();
});

function highlightActiveNav() {
  const path = window.location.pathname;
  const links = document.querySelectorAll('.navbar-menu .nav-item');

  links.forEach((link) => {
    // Clear any server-side class if present
    link.classList.remove('active');

    const href = link.getAttribute('href');
    if (!href) return;

    // Mark current nav item active when pathname starts with its href
    if (path === href || path.startsWith(href + '/')) {
      link.classList.add('active');
    }
  });
}
