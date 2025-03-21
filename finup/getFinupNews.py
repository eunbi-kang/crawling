import requests
from bs4 import BeautifulSoup
import time
import random

def get_news_from_finup(stock_code: str):
    # base_url = f"https://finance.finup.co.kr/Stock/{stock_code}"


    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    news_list = []

    # 뉴스 영역 탐색 (실제 구조에 따라 바꿔야 함)
    news_section = soup.select("div.news-area li")  # 구조 확인 필요

    for news in news_section:
        title_tag = news.select_one("a")
        date_tag = news.select_one("span.date")  # 구조 확인 필요

        if title_tag and date_tag:
            news_data = {
                "title": title_tag.text.strip(),
                "url": title_tag['href'],
                "date": date_tag.text.strip(),
                "stock_code": stock_code,
                "sentiment": "unknown"  # 이후 라벨링 예정
            }
            news_list.append(news_data)

    return news_list
