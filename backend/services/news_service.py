import requests
from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET

NAVER_NEWS_URL = "https://openapi.naver.com/v1/search/news.json"

# 🔥 주식 관련 키워드
STOCK_KEYWORDS = ["주가", "실적", "증시", "전망", "투자", "목표가", "매출", "영업이익"]

def fetch_news(query: str, display: int = 10):
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }

    # 🔥 1단계: query 강화
    enhanced_query = f"{query} 주가 OR 실적 OR 전망"

    params = {
        "query": enhanced_query,
        "display": display,
        "sort": "date"
    }

    response = requests.get(NAVER_NEWS_URL, headers=headers, params=params)
    response.encoding = "utf-8"

    if response.status_code != 200:
        raise Exception(f"Naver API Error: {response.status_code}")

    data = response.json()

    news_list = []
    for item in data.get("items", []):
        news = {
            "title": clean_html(item["title"]),
            "description": clean_html(item["description"]),
            "link": item["link"],
            "pubDate": item["pubDate"]
        }
        news_list.append(news)

    # 🔥 2단계: 주식 관련 필터링
    filtered_news = []
    for news in news_list:
        text = news["title"] + " " + news["description"]
        if any(keyword in text for keyword in STOCK_KEYWORDS):
            filtered_news.append(news)

    # 🔥 3단계: 최대 5개만 반환
    return filtered_news[:5]


def clean_html(text: str):
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)