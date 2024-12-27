document.getElementById('password-update-btn').addEventListener('click', function(e) {
  if (!confirm('비밀번호를 수정하시겠습니까?')) {
      e.preventDefault();  
  }
});


document.getElementById('user-delete').addEventListener('click', function(e){
  if(!confirm('회원탈퇴 하시겠습니까?')){
    e.preventDefault();
  }
});