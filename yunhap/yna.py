import os
import time
import random
import json
import pickle
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient

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

# ✅ 이스케이프 문자 제거 함수
def clean_text(text):
    if text:
        text = text.strip()  # 앞뒤 공백 제거
        text = re.sub(r"\s*\n\s*", " ", text)  # 줄바꿈을 공백으로 변환 (마침표 추가 X)
        text = re.sub(r"\s*\t\s*", " ", text)  # 탭(\t)을 공백으로 변환
        text = re.sub(r"\s+", " ", text)  # 여러 개의 공백을 하나로 변환

        # 문장이 마침표 없이 끝난 경우에만 마침표 추가
        if text and not text.endswith((".", "?", "!", "”", "\"")):
            text += "."

        # 따옴표(")가 중복되지 않도록 정리
        text = text.replace(" .", ".").replace(" .\"", ".\"")

        return text.strip()
    return None


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

# ✅ 기존 파일 삭제
delete_existing_files()

while True:
    print(f"📄 {page} 페이지 크롤링 중...")
    url = f"{base_url}{page}?site=wholemenu_economy_depth02"
    browser.get(url)
    wait = WebDriverWait(browser, 15)

    # ✅ JavaScript 실행하여 동적 로딩 시도
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.uniform(5, 8))

    # ✅ 기사 목록 로딩 대기
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="container"]/div[2]/div[2]/div[1]/section/div/ul')))
        print("✅ 뉴스 섹션 감지 완료!")
    except:
        print("⚠️ 뉴스 섹션을 찾을 수 없습니다. 마지막 페이지일 가능성이 있습니다.")
        break

    # ✅ 뉴스 목록 가져오기
    news_section = browser.find_element(By.XPATH, '//*[@id="container"]/div[2]/div[2]/div[1]/section/div/ul')

    # 🔥 HTML 구조 확인 (디버깅용)
    html_content = news_section.get_attribute("outerHTML")
    soup = BeautifulSoup(html_content, "html.parser")

    # ✅ 최신 뉴스 크롤링
    news_items = []
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

        news_items.append({
            "title": title,
            "link": link,
            "date": date,
            "summary": summary,
            "image_url": image_url
        })

    # ✅ 전체 뉴스 리스트에 추가
    all_news.extend(news_items)

    # ✅ 다음 페이지 버튼이 있는지 확인
    try:
        next_button = browser.find_element(By.XPATH, '//a[@class="next"]')
        next_page_url = next_button.get_attribute("href")

        if not next_page_url:
            print("🚪 다음 페이지가 없습니다. 크롤링 종료.")
            break

        page += 1
    except:
        print("🚪 다음 페이지 버튼을 찾을 수 없습니다. 크롤링 종료.")
        break

# ✅ 크롤링된 데이터를 데이터프레임으로 변환
df = pd.DataFrame(all_news)

# ✅ CSV 저장 (MongoDB 및 SQL Import-Friendly)
csv_path = os.path.join(DATA_DIR, "latest_news.csv")
df.to_csv(csv_path, index=False, encoding="utf-8-sig", na_rep="NULL", quotechar='"', doublequote=True)

# ✅ JSON 저장 (MongoDB Import-Friendly)
json_path = os.path.join(DATA_DIR, "latest_news.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=4)

# ✅ Pickle 저장 (Python 객체 그대로 저장, 성능 최적화)
pkl_path = os.path.join(DATA_DIR, "latest_news.pkl")
with open(pkl_path, "wb") as f:
    pickle.dump(df, f, protocol=pickle.HIGHEST_PROTOCOL)

# ✅ MongoDB 저장
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["news_db"]
mongo_collection = mongo_db["latest_news"]

# ✅ 기존 데이터 삭제 (권한 문제 방지)
try:
    mongo_collection.delete_many({})
    print("🗑 MongoDB 기존 데이터 삭제 완료.")
except Exception as e:
    print(f"⚠️ MongoDB 데이터 삭제 오류 발생: {e}")

# ✅ 새 데이터 삽입
try:
    mongo_collection.insert_many(df.to_dict(orient="records"))
    print("✅ MongoDB 데이터 저장 완료.")
except Exception as e:
    print(f"⚠️ MongoDB 데이터 삽입 오류 발생: {e}")

print(f"✅ 총 {len(df)}개의 뉴스 기사가 수집되었습니다.")
print(f"📂 CSV 파일 저장 완료: {csv_path}")
print(f"📂 JSON 파일 저장 완료: {json_path}")
print(f"📂 Pickle 파일 저장 완료: {pkl_path}")
print("📂 MongoDB 저장 완료!")

# ✅ 브라우저 종료
browser.quit()
print("🚪 브라우저 종료 완료!")

# ✅ 크롤링된 데이터 확인
if not df.empty:
    print("🔍 크롤링된 데이터 미리보기:")
    print(df.head())
else:
    print("⚠️ 크롤링된 데이터가 없습니다. 확인이 필요합니다.")
