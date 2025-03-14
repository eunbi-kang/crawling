import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 저장할 폴더 지정
DATA_DIR = "data"

if __name__ == "__main__":
    # 저장 폴더가 없으면 생성
    os.makedirs(DATA_DIR, exist_ok=True)

    # 1. 웹 페이지 요청 및 HTML 파싱
    url = "https://www.hollys.co.kr/store/korea/korStore2.do"
    response = requests.get(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    # 2. 매장 정보 추출
    stores = [
        {
            "지역": cols[0].text.strip(),
            "매장명": cols[1].text.strip(),
            "현황": cols[2].text.strip(),
            "주소": cols[3].text.strip(),
            "서비스": ", ".join(img["alt"] for img in cols[4].find_all("img")),
            "전화번호": cols[5].text.strip(),
        }
        for row in soup.select("table.tbl_store tbody tr")
        if (cols := row.find_all("td")) and len(cols) >= 6
    ]

    # 데이터프레임 변환 및 저장
    df = pd.DataFrame(stores)
    df.to_csv(os.path.join(DATA_DIR, "hollys_stores.csv"), index=False, encoding="utf-8-sig")
    df.to_pickle(os.path.join(DATA_DIR, "hollys_stores.pkl"))
