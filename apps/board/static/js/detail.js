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
