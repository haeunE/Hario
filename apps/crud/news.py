import requests
from bs4 import BeautifulSoup

def crawl_naver_news(query="CJ", max_results=2):
    url = f"https://search.naver.com/search.naver?where=news&sm=tab_jum&query={query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"HTTP 요청 실패: {response.status_code}")
    
    soup = BeautifulSoup(response.text, "html.parser")
    news_items = []
    
    # 뉴스 항목 추출
    news_list = soup.find_all('div', class_='news_wrap', limit=max_results)
    
    for news in news_list:
        title_tag = news.find('a', class_='news_tit')  # 제목
        summary_tag = news.find('a', class_='api_txt_lines dsc_txt_wrap')  # 본문 요약
        image_tag = news.find('a', class_='dsc_thumb')  # 이미지가 포함된 a 태그
        
        if title_tag and summary_tag:
            title = title_tag.get('title')  # 제목 텍스트
            link = title_tag.get('href')   # 링크
            summary = summary_tag.text.strip()  # 본문 요약 텍스트
            
            # 이미지 URL 추출 (a 태그에서 이미지 링크 가져오기)
            image_url = None
            if image_tag:
                img_tag = image_tag.find('img')  # a 태그 안의 img 태그 찾기
                if img_tag:
                    image_url = img_tag.get('src')  # 이미지 src 속성 값 추출

            # 이미지를 가져올 수 없는 경우, 다른 방법으로 시도 (img 태그에서 직접 src 속성 추출)
            if not image_url:
                img_tag = news.find('img')  # 다른 img 태그에서 src 속성 추출
                if img_tag:
                    image_url = img_tag.get('src')
            
            news_items.append({'title': title, 'summary': summary, 'link': link, 'image': image_url})
    
    return news_items

# # 테스트 실행
# news_items = crawl_naver_news(query="CJ", max_results=2)
# print(news_items)
