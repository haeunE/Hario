$('.board-delete').on('click', (e) => {
  e.preventDefault();
  const boardId = e.target.dataset.boardId;  // dataset 사용
  const selection = e.target.dataset.boardSelection;  // dataset 사용

  // 삭제 확인
  if (!confirm("게시물 삭제하시겠습니까?"))
    return;

  $.ajax({
    type: "DELETE",
    url: "/board/delete/" + boardId,
    headers: {
      'X-CSRFToken': $('input[name="csrf_token"]').val()  // CSRF 토큰 추가
    },
  }).done((response) => {
    alert(response.message);  
    location.href = "/board/" + selection;  
  }).fail((error) => {
    console.log(error);
  });
});

// 댓글 js
const commentObject ={
  init:function(){
   $('.comment-update-btn').on('click',(e)=>{
    e.preventDefault()
    const commentId = e.target.dataset.commentId;
    this.toggleEdit(commentId, true);
   }),
   $('.comment-save-btn').on('click', (e)=>{
    e.preventDefault()
    const commentId = e.target.dataset.commentId;
    const content = $(`[data-comment-id="${commentId}"]`).val();

    this.commentUpdate(commentId, content);
    this.toggleEdit(commentId, false);
   }),
   $('.comment-delete-btn').on('click', (e)=>{
    e.preventDefault()
    const commentId = e.target.dataset.commentId;
    this.commentDelete(commentId);
   })
  },

  toggleEdit : function(commentId, editMode){
    const commentItem = $(`[data-comment-id="${commentId}"]`);  
    // 수정 취소 시 원래 내용 복원
    const originalContent = commentItem.closest('.comment-items').find('.comment-content-show').text().trim();

    if(editMode){
      commentItem.closest('.comment-items').find('.comment-content-show').hide();
      commentItem.closest('.comment-items').find('.comment-update-btn').hide();
      commentItem.closest('.comment-items').find('.new-content').show();
      commentItem.closest('.comment-items').find('.comment-save-btn').show();
      commentItem.closest('.comment-items').find('.comment-delete-btn').show();
    }else{
      commentItem.closest('.comment-items').find('.comment-content-show').show();
      commentItem.closest('.comment-items').find('.comment-update-btn').show();
      commentItem.closest('.comment-items').find('.new-content').hide();
      commentItem.closest('.comment-items').find('.comment-save-btn').hide();
      commentItem.closest('.comment-items').find('.comment-delete-btn').hide();

      commentItem.closest('.comment-items').find('.new-content').val(originalContent);
    }
  },

  commentUpdate : function(commentId, content){

    if(!content){
      alert('수정할 내용을 넣어주세요.');
      return;
    }

    if(!confirm('수정 하시겠습니까?'))
      return;

    $.ajax({
      type : 'PUT',
      url : '/board/comment/update/' + commentId,
      data : JSON.stringify({content:content}),
      contentType : 'application/json; charset=uft-8',
      headers: {
        'X-CSRFToken': $('input[name="csrf_token"]').val()  // CSRF 토큰 추가
      },
    }).done(function(response){
      alert('수정되었습니다.');
      location.reload();
    }).fail(function(error){
      console.log(error);
    });
  },

  commentDelete : function(commentId){
    if(!confirm('삭제 하시겠습니까?'))
      return;
    $.ajax({
      type : 'DELETE',
      url : '/board/comment/delete/' + commentId,
      headers: {
        'X-CSRFToken': $('input[name="csrf_token"]').val()  // CSRF 토큰 추가
      },
    }).done(function(response){
      alert('삭제되었습니다.');
      location.reload();
    }).fail(function(error){
      console.log(error);
    });
  }
  
}

commentObject.init()

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
