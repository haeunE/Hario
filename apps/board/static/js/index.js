const urlParams = new URLSearchParams(window.location.search);
const departmentId = urlParams.get('department_id');

// department_id 값이 있으면, 해당 값에 맞게 select 옵션을 선택합니다
if (departmentId) {
  document.querySelector(`select[name="department_id"]`).value = departmentId;
}

// 완전히 로드되기 전에 스크립트가 실행되면 page-link 요소를 찾을 수 없으므로, DOM 로드 후에 동작을 설정
document.addEventListener('DOMContentLoaded', function(){
  const pageLinks = document.querySelectorAll('.page-link');

  pageLinks.forEach(link => {
    link.addEventListener('click', function(e){
      e.preventDefault();

       // 모든 링크에서 active 클래스 제거
       pageLinks.forEach(l => l.classList.remove('active-page'));

       // 클릭한 링크에 active 클래스 추가
       this.classList.add('active-page');
        
       // 실제 페이지 이동은 필요 시 여기에 추가
       window.location.href = this.href;
    });
  });
});