// register.js
//
// 회원가입 페이지(register.html)의 클라이언트 측 JavaScript 로직을 정의합니다.
// - 아이디 중복 확인, 비밀번호 일치 확인, 폼 데이터 유효성 검사 및 제출을 처리합니다.
//

let idChecked = false; // 아이디 중복 확인 여부를 저장하는 플래그

// --- 아이디 중복 확인 ---
async function checkDuplicate() {
    const id = document.getElementById('id').value; // 아이디 입력 필드 값
    const message = document.getElementById('idMessage'); // 메시지를 표시할 span 요소
    
    if (!id) {
        message.textContent = '아이디를 입력하세요.';
        message.className = 'form-message error'; // 에러 스타일 적용
        return;
    }
    
    try {
        // '/api/v1/account/check' API를 호출하여 아이디 중복 여부를 확인합니다.
        const response = await fetch('/api/v1/account/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ id: id }) // 아이디만 포함하여 요청
        });
        
        const data = await response.json(); // 응답을 JSON으로 파싱
        
        if (data.available) { // API 응답이 'available: true'이면 사용 가능한 아이디입니다.
            message.textContent = '✓ 사용 가능한 아이디입니다.';
            message.className = 'form-message success'; // 성공 스타일 적용
            idChecked = true; // 중복 확인 성공 플래그
            updateSubmitButton(); // 제출 버튼 상태 업데이트
        } else { // 'available: false'이면 이미 사용 중인 아이디입니다.
            message.textContent = '이미 사용 중인 아이디입니다.';
            message.className = 'form-message error'; // 에러 스타일 적용
            idChecked = false; // 중복 확인 실패 플래그
            updateSubmitButton(); // 제출 버튼 상태 업데이트
        }
    } catch (error) {
        console.error('Error:', error); // 에러 발생 시 콘솔에 기록
        message.textContent = '중복 확인 중 오류가 발생했습니다.';
        message.className = 'form-message error';
    }
}

// --- 아이디 입력 변경 시 처리 ---
// 아이디 입력 필드의 내용이 변경되면, 중복 확인 상태를 초기화하고 제출 버튼을 비활성화합니다.
document.getElementById('id').addEventListener('input', function() {
    idChecked = false; // 중복 확인 상태 초기화
    document.getElementById('idMessage').textContent = ''; // 메시지 지우기
    updateSubmitButton(); // 제출 버튼 상태 업데이트
});

// --- 비밀번호 확인 필드 입력 변경 시 처리 ---
// 비밀번호 확인 필드의 내용이 변경될 때마다 비밀번호 일치 여부를 검사합니다.
document.getElementById('pwd_confirm').addEventListener('input', function() {
    const pwd = document.getElementById('pwd').value; // 비밀번호 입력 필드 값
    const pwdConfirm = this.value; // 비밀번호 확인 필드 값
    const message = document.getElementById('pwdMessage'); // 메시지를 표시할 span 요소
    
    if (pwdConfirm && pwd !== pwdConfirm) { // 비밀번호가 입력되었지만 일치하지 않는 경우
        message.textContent = '비밀번호가 일치하지 않습니다.';
        message.className = 'form-message error';
    } else if (pwdConfirm && pwd === pwdConfirm) { // 비밀번호가 일치하는 경우
        message.textContent = '✓ 비밀번호가 일치합니다.';
        message.className = 'form-message success';
    } else { // 비밀번호 확인 필드가 비어있거나 아직 입력 중인 경우
        message.textContent = '';
    }
    
    updateSubmitButton(); // 제출 버튼 상태 업데이트
});

// --- 제출 버튼 활성화/비활성화 로직 ---
// 회원가입 제출 버튼의 활성화/비활성화 상태를 업데이트합니다.
// 아이디 중복 확인, 비밀번호 일치 및 입력 여부가 모두 충족되어야 활성화됩니다.
function updateSubmitButton() {
    const pwd = document.getElementById('pwd').value; // 비밀번호
    const pwdConfirm = document.getElementById('pwd_confirm').value; // 비밀번호 확인
    const submitBtn = document.getElementById('submitBtn'); // 제출 버튼
    
    // 아이디 중복 확인 완료(idChecked), 비밀번호 입력됨, 비밀번호 확인 입력됨, 두 비밀번호 일치
    if (idChecked && pwd && pwdConfirm && pwd === pwdConfirm) {
        submitBtn.disabled = false; // 버튼 활성화
    } else {
        submitBtn.disabled = true; // 버튼 비활성화
    }
}

// --- 회원가입 폼 제출 처리 ---
// 'registerForm' 제출 이벤트 리스너
document.getElementById('registerForm').addEventListener('submit', async function(e) {
    e.preventDefault(); // 폼 기본 제출 동작 방지
    
    // 아이디 중복 확인이 완료되지 않았다면 경고 메시지 표시
    if (!idChecked) {
        alert('아이디 중복 확인을 해주세요.');
        return;
    }
    
    // 폼에서 모든 입력 값을 가져와 formData 객체 생성
    const formData = {
        id: document.getElementById('id').value,
        pwd: document.getElementById('pwd').value,
        name: document.getElementById('name').value,
        department: document.getElementById('department').value,
        position: document.getElementById('position').value,
        phone_number: document.getElementById('phone_number').value,
        e_mail: document.getElementById('e_mail').value
    };
    
    try {
        // '/api/v1/account/register' API를 호출하여 회원가입을 시도합니다.
        const response = await fetch('/api/v1/account/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData) // 폼 데이터를 JSON 형식으로 전송
        });
        
        if (response.ok) { // 응답 상태 코드가 200번대이면 성공
            const data = await response.json(); // 응답을 JSON으로 파싱
            alert('회원가입이 완료되었습니다!');
            window.location.href = '/login'; // 로그인 페이지로 이동
        } else { // 응답 상태 코드가 에러인 경우
            const error = await response.json(); // 에러 메시지를 JSON으로 파싱
            alert('회원가입 실패: ' + (error.detail || '알 수 없는 오류')); // 사용자에게 에러 메시지 표시
        }
    } catch (error) {
        console.error('Error:', error); // 에러 발생 시 콘솔에 기록
        alert('회원가입 중 오류가 발생했습니다.'); // 사용자에게 에러 메시지 표시
    }
});