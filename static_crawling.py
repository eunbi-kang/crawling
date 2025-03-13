import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 저장할 폴더 지정
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# 기본 URL 설정
BASE_URL = "https://www.hollys.co.kr/store/korea/korStore2.do"

# User-Agent 설정 (웹사이트 차단 방지)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

def get_store_data(page: int) -> list:
    """ 특정 페이지의 매장 데이터를 크롤링하여 리스트로 반환 """
    url = f"{BASE_URL}?pageNo={page}&sido=&gugun=&store="

    # 웹 페이지 요청 (User-Agent 추가)
    response = requests.get(url, headers=HEADERS)

    # 응답 코드 확인
    if response.status_code != 200:
        print(f"❌ 요청 실패 (페이지 {page}, 상태 코드: {response.status_code})")
        return None

    # HTML 파싱
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    # ✅ 변경된 테이블 선택자 적용
    table = soup.select_one("table.tb_store")
    if not table:
        print(f"❌ 테이블을 찾을 수 없음 (페이지 {page})")
        return None

    rows = table.select("tbody tr")

    # ✅ 데이터가 없으면 크롤링 중단
    if not rows:
        print(f"🚫 페이지 {page}에 더 이상 매장이 없음, 크롤링 중단!")
        return None

    # 리스트 컴프리헨션을 이용한 최적화된 크롤링
    stores = [
        {
            "지역": cols[0].text.strip(),
            "매장명": cols[1].text.strip(),
            "현황": cols[2].text.strip(),
            "주소": cols[3].text.strip(),
            "서비스": ", ".join(img["alt"] for img in cols[4].find_all("img")),
            "전화번호": cols[5].text.strip(),
        }
        for row in rows if (cols := row.find_all("td")) and len(cols) >= 6
    ]

    # ✅ 매장 데이터가 0개면 크롤링 중단
    if len(stores) == 0:
        print(f"🚫 페이지 {page}에 매장이 없음, 크롤링 중단!")
        return None

    return stores


def scrape_all_pages():
    """ 모든 페이지를 크롤링하고 하나의 CSV 및 PKL 파일에 저장 """
    all_stores = []
    page = 1

    while True:
        stores = get_store_data(page)

        # ✅ 더 이상 데이터가 없으면 종료
        if stores is None:
            print(f"✅ 마지막 페이지 {page - 1}까지 크롤링 완료!")
            break

        all_stores.extend(stores)
        print(f"📄 페이지 {page} 크롤링 완료 ({len(stores)}개 매장)")
        page += 1  # 다음 페이지로 이동

    # 전체 데이터를 하나의 CSV 및 PKL 파일로 저장
    if all_stores:
        df_total = pd.DataFrame(all_stores)
        df_total.to_csv(os.path.join(DATA_DIR, "hollys_stores.csv"), index=False, encoding="utf-8-sig")
        df_total.to_pickle(os.path.join(DATA_DIR, "hollys_stores.pkl"))
        print(f"📁 전체 데이터 저장 완료 (총 {len(all_stores)}개 매장)")

if __name__ == "__main__":
    scrape_all_pages()
