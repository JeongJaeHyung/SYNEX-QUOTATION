document.addEventListener('DOMContentLoaded', () => {
  highlightActiveNav();
  loadSettings();
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

// ========================================
// 설정 관련 함수
// ========================================

let appSettings = {
  pdfSavePath: '',
  askSaveLocation: false
};

// 설정 모달 열기
function openSettingsModal() {
  const modal = document.getElementById('settingsModal');
  const pathInput = document.getElementById('pdfSavePath');
  const askCheckbox = document.getElementById('askSaveLocation');

  if (pathInput && appSettings.pdfSavePath) {
    pathInput.value = appSettings.pdfSavePath;
  }
  if (askCheckbox) {
    askCheckbox.checked = appSettings.askSaveLocation || false;
  }

  if (modal) {
    modal.style.display = 'flex';
  }
}

// 설정 모달 닫기
function closeSettingsModal() {
  const modal = document.getElementById('settingsModal');
  if (modal) {
    modal.style.display = 'none';
  }
}

// 설정 로드
async function loadSettings() {
  try {
    const response = await fetch('/api/settings');
    if (response.ok) {
      appSettings = await response.json();
      const pathInput = document.getElementById('pdfSavePath');
      if (pathInput && appSettings.pdfSavePath) {
        pathInput.value = appSettings.pdfSavePath;
      }
    }
  } catch (error) {
    console.log('설정 로드 실패:', error);
  }
}

// 설정 저장
async function saveSettings() {
  const pathInput = document.getElementById('pdfSavePath');
  const askCheckbox = document.getElementById('askSaveLocation');

  appSettings.pdfSavePath = pathInput ? pathInput.value : '';
  appSettings.askSaveLocation = askCheckbox ? askCheckbox.checked : false;

  try {
    const response = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(appSettings)
    });

    if (response.ok) {
      alert('설정이 저장되었습니다.');
      closeSettingsModal();
    } else {
      alert('설정 저장에 실패했습니다.');
    }
  } catch (error) {
    console.error('설정 저장 오류:', error);
    alert('설정 저장 중 오류가 발생했습니다.');
  }
}

// 폴더 선택
async function selectPdfFolder() {
  try {
    const response = await fetch('/api/select-folder');
    const result = await response.json();

    if (result.success && result.path) {
      const pathInput = document.getElementById('pdfSavePath');
      if (pathInput) {
        pathInput.value = result.path;
      }
    }
  } catch (error) {
    console.error('폴더 선택 오류:', error);
  }
}

// 모달 외부 클릭 시 닫기
document.addEventListener('click', (e) => {
  const modal = document.getElementById('settingsModal');
  if (e.target === modal) {
    closeSettingsModal();
  }
});

// ESC 키로 모달 닫기
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeSettingsModal();
  }
});
