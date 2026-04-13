import requests
from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET

NAVER_NEWS_URL = "https://openapi.naver.com/v1/search/news.json"

def fetch_news(query: str, display: int = 5):
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }

    params = {
        "query": query,
        "display": display,
        "sort": "date"
    }

    response = requests.get(NAVER_NEWS_URL, headers=headers, params=params)

    response.encoding = "utf-8"

    if response.status_code != 200:
        raise Exception(f"Naver API Error: {response.status_code}")

    data = response.json()

    print("RAW DATA:", data)
    print("ITEMS:", data.get("items"))

    news_list = []
    for item in data.get("items", []):
        news = {
            "title": clean_html(item["title"]),
            "description": clean_html(item["description"]),
            "link": item["link"],
            "pubDate": item["pubDate"]
        }
        news_list.append(news)

    print("PARSED NEWS:", news_list)

    return news_list

def clean_html(text: str):
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)