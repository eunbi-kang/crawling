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

# ✅ 데이터 저장 폴더 설정 (../data)
DATA_DIR = "../data"
os.makedirs(DATA_DIR, exist_ok=True)

# ✅ 기존 파일 삭제 함수
def delete_existing_files():
    csv_path = os.path.join(DATA_DIR, "latest_news.csv")
    pkl_path = os.path.join(DATA_DIR, "latest_news.pkl")

    if os.path.exists(csv_path):
        os.remove(csv_path)
        print(f"🗑 기존 CSV 파일 삭제: {csv_path}")

    if os.path.exists(pkl_path):
        os.remove(pkl_path)
        print(f"🗑 기존 PKL 파일 삭제: {pkl_path}")

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

# ✅ 크롤링할 기본 URL
base_url = "https://www.yna.co.kr/economy/real-estate/"
page = 1  # 시작 페이지
all_news = []  # 전체 뉴스 저장 리스트

# ✅ 기존 파일 삭제
delete_existing_files()

while True:
    print(f"📄 {page} 페이지 크롤링 중...")
    url = f"{base_url}{page}?site=wholemenu_economy_depth02"
    browser.get(url)
    wait = WebDriverWait(browser, 15)

    # ✅ JavaScript 실행하여 동적 로딩 시도
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # 맨 아래로 스크롤
    time.sleep(random.uniform(5, 8))  # ✅ JavaScript 실행 후 대기

    # ✅ 기사 목록이 있는 `list01`이 로드될 때까지 대기
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="container"]/div[2]/div[2]/div[1]/section/div/ul')))
        print("✅ 뉴스 섹션 감지 완료!")
    except:
        print("⚠️ 뉴스 섹션을 찾을 수 없습니다. 마지막 페이지일 가능성이 있습니다.")
        break

    # ✅ 뉴스 목록 가져오기 (item-box01 내부의 데이터 크롤링)
    news_section = browser.find_element(By.XPATH, '//*[@id="container"]/div[2]/div[2]/div[1]/section/div/ul')

    # 🔥 HTML 구조 확인 (디버깅용)
    html_content = news_section.get_attribute("outerHTML")
    print("\n🔍 현재 뉴스 섹션 HTML 구조:\n", html_content[:1000])  # ✅ HTML 일부 확인 (1000자 제한)

    soup = BeautifulSoup(html_content, "html.parser")

    # ✅ 최신 뉴스 크롤링
    news_items = []
    articles = soup.select("div.item-box01")  # ✅ 뉴스 기사 리스트

    if not articles:
        print("⚠️ 'item-box01' 내부에서 기사를 찾지 못했습니다. HTML 구조 변경 가능성 있음.")

    for article in articles:
        title_tag = article.select_one("a.tit-news span.title01")  # ✅ 기사 제목
        link_tag = article.select_one("a.tit-news")  # ✅ 기사 링크
        date_tag = article.select_one("span.txt-time")  # ✅ 날짜
        summary_tag = article.select_one("p.lead")  # ✅ 요약

        title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
        link = link_tag["href"] if link_tag and "href" in link_tag.attrs else "링크 없음"
        date = date_tag.get_text(strip=True) if date_tag else "날짜 없음"
        summary = summary_tag.get_text(strip=True) if summary_tag else "요약 없음"

        news_items.append({
            "title": title,
            "link": f"https://www.yna.co.kr{link}" if "링크 없음" not in link else None,
            "date": date,
            "summary": summary
        })

    # ✅ 전체 뉴스 리스트에 추가
    all_news.extend(news_items)

    # ✅ 다음 페이지 버튼이 있는지 확인
    try:
        next_button = browser.find_element(By.XPATH, '//a[@class="next"]')
        next_page_url = next_button.get_attribute("href")

        if not next_page_url:
            print("🚪 다음 페이지가 없습니다. 크롤링 종료.")
            break  # 더 이상 페이지가 없으면 종료

        page += 1  # 다음 페이지로 이동
    except:
        print("🚪 다음 페이지 버튼을 찾을 수 없습니다. 크롤링 종료.")
        break

# ✅ 크롤링된 데이터를 데이터프레임으로 변환
df = pd.DataFrame(all_news)

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

# ✅ 크롤링된 데이터 확인 (일반 Python 환경에서도 가능)
if not df.empty:
    print("🔍 크롤링된 데이터 미리보기:")
    print(df.head())  # ✅ 일반 Python 환경에서도 실행 가능
else:
    print("⚠️ 크롤링된 데이터가 없습니다. 확인이 필요합니다.")
