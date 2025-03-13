import os
import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

# ✅ 데이터 저장 폴더 설정
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ✅ Selenium WebDriver 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 브라우저 창을 띄우지 않음
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-dev-shm-usage")

# ✅ WebDriver 실행
service = Service(ChromeDriverManager().install())
browser = webdriver.Chrome(service=service, options=chrome_options)

# ✅ 크롤링할 URL
url = "https://www.yna.co.kr/economy/real-estate?site=wholemenu_economy_depth02"
browser.get(url)
wait = WebDriverWait(browser, 15)  # 최대 15초까지 대기

# ✅ JavaScript 실행하여 동적 로딩 시도 (이벤트 트리거)
browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # 맨 아래로 스크롤
time.sleep(random.uniform(5, 8))  # ✅ JavaScript 실행 후 대기

# ✅ 정확한 XPath를 사용하여 `container512` 찾기
try:
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="container"]/div[2]')))
    print("✅ 뉴스 섹션 감지 완료!")
except:
    print("⚠️ 뉴스 섹션을 찾을 수 없습니다. HTML 구조 변경 가능성 있음.")
    browser.quit()
    exit()

# ✅ `container512` 요소 가져오기
news_section = browser.find_element(By.XPATH, '//*[@id="container"]/div[2]')

# ✅ BeautifulSoup으로 HTML 파싱
soup = BeautifulSoup(news_section.get_attribute("outerHTML"), "html.parser")

# ✅ 최신 뉴스 크롤링
news_items = []
articles = soup.find_all("li")  # 뉴스 목록
for article in articles:
    title_tag = article.find("a", class_="tit-news")
    date_tag = article.find("span", class_="txt-time")
    summary_tag = article.find("p", class_="lead")

    title = title_tag.get_text(strip=True) if title_tag else None
    link = title_tag["href"] if title_tag and "href" in title_tag.attrs else None
    date = date_tag.get_text(strip=True) if date_tag else None
    summary = summary_tag.get_text(strip=True) if summary_tag else None

    news_items.append({
        "title": title,
        "link": f"https://www.yna.co.kr{link}" if link else None,
        "date": date,
        "summary": summary
    })

# ✅ 크롤링된 데이터를 데이터프레임으로 변환
df = pd.DataFrame(news_items)

# ✅ CSV 저장
csv_path = os.path.join(DATA_DIR, "latest_news.csv")
df.to_csv(csv_path, index=False, encoding="utf-8-sig")

# ✅ PKL 저장
pkl_path = os.path.join(DATA_DIR, "latest_news.pkl")
df.to_pickle(pkl_path)

print(f"✅ 총 {len(df)}개의 뉴스 기사가 수집되었습니다.")
print(f"📂 CSV 파일 저장 완료: {csv_path}")
print(f"📂 PKL 파일 저장 완료: {pkl_path}")

# ✅ 브라우저 종료
browser.quit()
print("🚪 브라우저 종료 완료!")
