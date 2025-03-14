import sys
import time
import random
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

# 🔥 sys.path 추가하여 crawling 경로에서 실행 가능하도록 설정
sys.path.append("..")

# 🔥 올바른 경로에서 driver 가져오기
from dynamic_crawling import driver

def scrape_page_data(browser):
    """ 현재 페이지의 매장 정보를 크롤링하여 리스트 반환 """
    trs = BeautifulSoup(browser.page_source, 'html.parser').find_all("tr")
    page_data = []

    for row in trs:
        cols = row.find_all("td")
        if len(cols) >= 6:
            data = {
                "지역": cols[0].text.strip(),
                "매장명": cols[1].text.strip(),
                "현황": cols[2].text.strip(),
                "주소": cols[3].text.strip(),
                "서비스": ", ".join(img["alt"] for img in cols[4].find_all("img")),
                "전화번호": cols[5].text.strip()
            }
            page_data.append(data)

    return page_data

if __name__ == "__main__":
    url = "https://www.hollys.co.kr/store/korea/korStore2.do?a=2&b=3"
    browser = driver()  # ✅ driver() 함수 호출
    browser.get(url)
    time.sleep(random.uniform(2, 4))

    # ✅ 크롤링할 데이터 저장 리스트
    all_data = []
    total_pages = 49  # 🔥 전체 페이지 수
    page = 1

    while page <= total_pages:
        try:
            print(f"🔄 {page} 페이지 크롤링 중...")

            # ✅ 현재 페이지 크롤링
            page_data = scrape_page_data(browser)
            if not page_data:
                print(f"⛔ {page} 페이지에 데이터가 없습니다. 크롤링 종료.")
                break

            all_data.extend(page_data)

            time.sleep(random.uniform(2, 4))  # ✅ 대기 시간 추가 (서버 부하 방지)

            # ✅ 다음 페이지로 이동
            if page % 10 == 0 and page < total_pages:
                # 🔥 '다음10개' 버튼 클릭
                try:
                    next_button = browser.find_element(By.XPATH, "//a[contains(@onclick, 'paging')]/img[@alt='다음10개']/parent::a")
                    next_button.click()
                    print(f"➡️ '다음10개' 버튼 클릭하여 새로운 페이지 그룹 로드")
                except:
                    print("⛔ '다음10개' 버튼이 없습니다. 크롤링 종료.")
                    break
            else:
                # 🔥 개별 페이지 버튼 클릭
                try:
                    next_page = browser.find_element(By.XPATH, f"//a[contains(@onclick, 'paging({page + 1})')]")
                    next_page.click()
                    print(f"➡️ {page + 1} 페이지로 이동")
                except:
                    print(f"⛔ {page + 1} 페이지 버튼이 없습니다. 크롤링 종료.")
                    break

            page += 1
            time.sleep(random.uniform(2, 4))  # ✅ 페이지 로딩 대기

        except Exception as e:
            print(f"⛔ 페이지 이동 실패: {e}")
            break  # 더 이상 페이지가 없으면 종료

    # ✅ 크롤링 완료된 데이터 CSV로 저장
    df = pd.DataFrame(all_data)
    df.to_csv("hollys_stores.csv", index=False, encoding="utf-8-sig")
    print(f"✅ 총 {len(all_data)}개 매장 데이터 저장 완료! (CSV)")

    # ✅ 크롤링 데이터를 `.pkl` 파일로 저장
    df.to_pickle("hollys_stores.pkl")
    print(f"✅ 총 {len(all_data)}개 매장 데이터 저장 완료! (PKL)")

    browser.quit()  # ✅ 브라우저 닫기 추가
    print("🚪 브라우저 종료 완료!")
