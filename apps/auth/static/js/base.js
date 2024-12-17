 // 스크롤 업 버튼 제어
 const scrollToTopButton = document.getElementById("scrollToTop");

 // 페이지가 일정 높이 이상 스크롤 되면 버튼 표시
 window.onscroll = function() {
   if (document.body.scrollTop > 200 || document.documentElement.scrollTop > 200) {
     scrollToTopButton.style.display = "block";
   } else {
     scrollToTopButton.style.display = "none";
   }
 };

 // 버튼 클릭 시 페이지 상단으로 스크롤
 scrollToTopButton.onclick = function() {
   window.scrollTo({ top: 0, behavior: "smooth" });
 };
 