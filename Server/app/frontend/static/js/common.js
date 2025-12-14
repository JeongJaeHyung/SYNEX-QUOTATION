// Common UI helpers shared across pages

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
