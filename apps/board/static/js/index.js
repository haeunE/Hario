const urlParams = new URLSearchParams(window.location.search);
const departmentId = urlParams.get('department_id');

// department_id 값이 있으면, 해당 값에 맞게 select 옵션을 선택합니다
if (departmentId) {
  document.querySelector(`select[name="department_id"]`).value = departmentId;
}