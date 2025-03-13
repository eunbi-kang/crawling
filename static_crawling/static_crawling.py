import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm  # ✅ 진행 상태 표시용 라이브러리
from colorama import Fore


# 데이터 저장 폴더 생성
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# 기본 URL 및 요청 헤더 설정
BASE_URL = "https://www.hollys.co.kr/store/korea/korStore2.do"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

def get_store_data(page):
    """ 특정 페이지의 매장 데이터를 리스트로 반환 """
    response = requests.get(f"{BASE_URL}?pageNo={page}&sido=&gugun=&store=", headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    return [
        { "지역": cols[0].text.strip(), "매장명": cols[1].text.strip(), "현황": cols[2].text.strip(),
          "주소": cols[3].text.strip(), "서비스": ", ".join(img["alt"] for img in cols[4].find_all("img")),
          "전화번호": cols[5].text.strip() }
        for row in soup.select("table.tb_store tbody tr")
        if (cols := row.find_all("td")) and len(cols) >= 6
    ]

def scrape_all_pages():
    """ 모든 페이지를 크롤링하여 CSV로 저장 (진행상황 tqdm 표시) """
    all_stores, page = [], 1

    with tqdm(desc=Fore.GREEN + "페이지 수집 진행", colour='cyan', dynamic_ncols=True) as pbar:
        while (stores := get_store_data(page)):
            all_stores.extend(stores)
            pbar.update(1)  # ✅ tqdm 업데이트
            pbar.set_postfix({"페이지": page, "수집 매장": len(stores)})
            page += 1

    pd.DataFrame(all_stores).to_csv(os.path.join(DATA_DIR, "hollys_stores.csv"), index=False, encoding="utf-8-sig")
    print(f"\n📁 총 {len(all_stores)}개 매장 데이터 저장 완료!")

if __name__ == "__main__":
    scrape_all_pages()
