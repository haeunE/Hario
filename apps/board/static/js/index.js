const urlParams = new URLSearchParams(window.location.search);
const departmentId = urlParams.get('department_id');

// department_id 값이 있으면, 해당 값에 맞게 select 옵션을 선택합니다
if (departmentId) {
  document.querySelector(`select[name="department_id"]`).value = departmentId;
}

// 완전히 로드되기 전에 스크립트가 실행되면 page-link 요소를 찾을 수 없으므로, DOM 로드 후에 동작을 설정
document.addEventListener('DOMContentLoaded', function() {
  const pageLinks = document.querySelectorAll('.page-link');

  // 페이지 링크를 순회하면서 active 페이지를 설정
  function updateActivePage() {
    const currentPage = new URL(window.location.href).searchParams.get('page') || 1;  // URL에서 page 값 추출

    pageLinks.forEach(link => {
      const page = new URL(link.href).searchParams.get('page');
      if (page === currentPage) {
        link.classList.add('active-page');
      } else {
        link.classList.remove('active-page');
      }
    });
  }

  // 페이지 링크 클릭 시 페이지 이동
  pageLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const url = this.href;
      window.history.pushState({}, '', url);  // URL을 변경하지만 페이지는 새로 고침하지 않음
      updateActivePage();  // 클릭한 링크에 active-page 클래스 추가
      window.location.href = url;  // 페이지 이동
    });
  });

  // 페이지 이동 시 popstate 이벤트로 active-page 업데이트
  window.addEventListener('popstate', function() {
    updateActivePage();  // 뒤로 가기/앞으로 가기 시 active-page 클래스 업데이트
  });

  // 초기 로딩 시 active-page 클래스 업데이트
  updateActivePage();
});