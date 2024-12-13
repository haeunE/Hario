// HTML에서 'data-*' 속성으로 이미지를 전달받기
const subsidiaryData = document.getElementById('subsidiary-data');

const subsidiaries = [
  { name: "CJ 대한통운", link: "https://www.cjlogistics.com/", logo: subsidiaryData.dataset.cjlogistics },
  { name: "CJ 제일제당", link: "https://www.cj.co.kr/", logo: subsidiaryData.dataset.cheil },
  { name: "CJ 프레시웨이", link: "https://www.freshway.co.kr/", logo: subsidiaryData.dataset.freshway },
  { name: "CJ ENM", link: "https://www.cjenm.com/", logo: subsidiaryData.dataset.cjenm },
  { name: "CGV", link: "https://www.cgv.co.kr/", logo: subsidiaryData.dataset.cgv },
  { name: "스튜디오드래곤", link: "https://www.studiodragon.net/", logo: subsidiaryData.dataset.studio },
  { name: "CJ 씨푸드", link: "https://www.cjseafood.net/", logo: subsidiaryData.dataset.seafood },
  { name: "CJ 바이오사이언스", link: "https://www.cjbio.net/", logo: subsidiaryData.dataset.bioscience },
];

// 슬라이더 트랙에 아이템 추가
const sliderTrack = document.querySelector(".slider-track");

// 반복문으로 슬라이더 아이템 생성
subsidiaries.forEach((subsidiary) => {
  const item = document.createElement("div");
  item.classList.add("subsidiary-item");

  item.innerHTML = `
      <button onclick="window.location.href='${subsidiary.link}'">
          <img src="${subsidiary.logo}" alt="${subsidiary.name} 로고">
      </button>
  `;
  sliderTrack.appendChild(item);
});

// 반복되는 아이템을 트랙에 추가하여 자연스럽게 연결
subsidiaries.forEach((subsidiary) => {
  const item = document.createElement("div");
  item.classList.add("subsidiary-item");

  item.innerHTML = `
      <button onclick="window.location.href='${subsidiary.link}'">
          <img src="${subsidiary.logo}" alt="${subsidiary.name} 로고">
      </button>
  `;
  sliderTrack.appendChild(item);
});


// document.addEventListener("DOMContentLoaded", function() {
//   // 최신 뉴스 데이터를 가져오는 함수
//   function fetchLatestNews() {
//       fetch('/latest-news')
//           .then(response => response.json())
//           .then(data => {
//               const newsContainer = document.getElementById('latest-news-container');
//               const lastUpdated = data.last_updated;
//               const articles = data.articles;

//               // 날짜 업데이트 표시
//               document.getElementById('last-updated').innerText = `최종 업데이트: ${lastUpdated}`;

//               // 뉴스 항목을 화면에 추가
//               newsContainer.innerHTML = '';  // 기존 내용 초기화

//               articles.forEach(article => {
//                   const articleElement = document.createElement('div');
//                   articleElement.classList.add('news-item');
//                   articleElement.innerHTML = `
//                       <h3><a href="${article.link}" target="_blank">${article.title}</a></h3>
//                       <p>${article.summary}</p>
//                   `;
//                   newsContainer.appendChild(articleElement);
//               });
//           })
//           .catch(error => {
//               console.error('뉴스를 가져오는 데 오류가 발생했습니다:', error);
//           });
//   }

//   // 뉴스 데이터를 로드
//   fetchLatestNews();
// });
