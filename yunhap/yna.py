import os
import time
import random
import json
import pickle
import pandas as pd
import re
import numpy as np
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from konlpy.tag import Mecab
from sentence_transformers import SentenceTransformer

# ✅ MongoDB 연결 설정
MONGO_URI = "mongodb://eunbikang:1234@localhost:27017/admin"
client = MongoClient(MONGO_URI)
db = client["admin"]
collection = db["latest_news"]

# ✅ SentenceTransformer 모델 로드 (벡터화)
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# ✅ Mecab 형태소 분석기 로드
mecab = Mecab()

# ✅ 데이터 저장 폴더 설정
DATA_DIR = "../data"
os.makedirs(DATA_DIR, exist_ok=True)

# ✅ 기존 파일 삭제 함수
def delete_existing_files():
    files_to_delete = ["latest_news.csv", "latest_news.json", "latest_news.pkl"]
    for file in files_to_delete:
        file_path = os.path.join(DATA_DIR, file)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑 기존 파일 삭제: {file_path}")

# ✅ ID 자동 증가 함수 (MongoDB에서 가장 큰 id 값 찾기)
def get_next_id():
    last_doc = collection.find_one(sort=[("id", -1)])  # 가장 큰 id 찾기
    return last_doc["id"] + 1 if last_doc else 1  # 데이터 없으면 1부터 시작

# ✅ 텍스트 정리 함수 (줄바꿈, 공백, 마침표 처리)
def clean_text(text):
    if text:
        text = text.strip()
        text = re.sub(r"\s*\n\s*", " ", text)  # 개행 → 공백 변환
        text = re.sub(r"\s*\t\s*", " ", text)  # 탭 → 공백 변환
        text = re.sub(r"\s+", " ", text)  # 연속된 공백 압축

        # 문장이 마침표 없이 끝나면 마침표 추가
        if text and not text.endswith((".", "?", "!", "”", "\"")):
            text += "."

        text = text.replace(" .", ".").replace(" .\"", ".\"")

        return text.strip()
    return None

# ✅ 형태소 분석 (키워드 추출)
def extract_keywords(text):
    tokens = mecab.nouns(text)  # 명사만 추출
    return " ".join(tokens)

# ✅ 벡터화 함수 (문장을 벡터로 변환)
def vectorize_text(text):
    return model.encode(text).tolist()

# ✅ 연합뉴스(부동산) 뉴스 크롤링 함수
def crawl_news():
    print("🔍 뉴스 크롤링 시작...")

    # ✅ Selenium WebDriver 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # ✅ WebDriver 실행
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=chrome_options)

    # ✅ 크롤링할 기본 URL
    base_url = "https://www.yna.co.kr/economy/real-estate/"
    page = 1
    all_news = []

    while page <= 2:  # ✅ 2페이지까지만 크롤링 (더 늘릴 수도 있음)
        print(f"📄 {page} 페이지 크롤링 중...")
        url = f"{base_url}{page}?site=wholemenu_economy_depth02"
        browser.get(url)
        wait = WebDriverWait(browser, 15)

        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(5, 8))

        try:
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="container"]/div[2]/div[2]/div[1]/section/div/ul')))
            print("✅ 뉴스 섹션 감지 완료!")
        except:
            print("⚠️ 뉴스 섹션을 찾을 수 없습니다. 마지막 페이지일 가능성이 있습니다.")
            break

        news_section = browser.find_element(By.XPATH, '//*[@id="container"]/div[2]/div[2]/div[1]/section/div/ul')
        html_content = news_section.get_attribute("outerHTML")
        soup = BeautifulSoup(html_content, "html.parser")

        articles = soup.select("div.item-box01")
        if not articles:
            print("⚠️ 'item-box01' 내부에서 기사를 찾지 못했습니다. HTML 구조 변경 가능성 있음.")

        for article in articles:
            title_tag = article.select_one("a.tit-news span.title01")
            link_tag = article.select_one("a.tit-news")
            date_tag = article.select_one("span.txt-time")
            summary_tag = article.select_one("p.lead")
            image_tag = article.select_one("figure.img-con01 img")

            title = clean_text(title_tag.get_text(strip=True)) if title_tag else None
            link = f"https://www.yna.co.kr{link_tag['href']}" if link_tag and "href" in link_tag.attrs else None
            date = clean_text(date_tag.get_text(strip=True)) if date_tag else None
            summary = clean_text(summary_tag.get_text(strip=True)) if summary_tag else None
            image_url = image_tag["src"] if image_tag and "src" in image_tag.attrs else None

            if summary:
                keywords = extract_keywords(summary)  # ✅ 키워드 추출
                vector = vectorize_text(keywords)  # ✅ 벡터화

                news_data = {
                    "id": get_next_id(),  # ✅ 자동 증가 ID 추가
                    "title": title,
                    "link": link,
                    "date": date,
                    "summary": summary,
                    "image_url": image_url,
                    "vector": vector
                }

                all_news.append(news_data)

        page += 1

    browser.quit()
    print(f"✅ 크롤링 완료! 총 {len(all_news)}개 뉴스 수집")

    return all_news

# ✅ MongoDB에 데이터 저장
def save_to_mongodb(news_list):
    if not news_list:
        print("⚠️ 저장할 뉴스가 없습니다!")
        return

    # ✅ 기존 데이터 삭제 (옵션)
    collection.delete_many({})
    print("🗑 기존 데이터 삭제 완료!")

    # ✅ 새 데이터 저장
    collection.insert_many(news_list)
    print(f"✅ {len(news_list)}개 뉴스 저장 완료!")

# ✅ 실행 (크롤링 → 벡터화 → MongoDB 저장)
if __name__ == "__main__":
    delete_existing_files()
    news_data = crawl_news()
    save_to_mongodb(news_data)

    # ✅ MongoDB 데이터 확인
    doc_count = collection.count_documents({})
    print(f"🔍 MongoDB 저장된 뉴스 개수: {doc_count}")
