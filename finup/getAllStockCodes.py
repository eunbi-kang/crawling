# 1. KOSPI	✅ 포함
# 2. KOSDAQ	✅ 포함
# 3. KONEX	✅ 포함
# 4. 비상장 (예: 스타트업, OTC)	❌ 미포함
import pandas as pd
import requests
import json
import os
from io import StringIO

def get_all_stock_codes():
    url = 'https://kind.krx.co.kr/corpgeneral/corpList.do?method=download'
    res = requests.get(url)
    res.encoding = 'euc-kr'

    html = StringIO(res.text)
    df = pd.read_html(html)[0]

    df = df[['회사명', '종목코드']]
    df['종목코드'] = df['종목코드'].apply(lambda x: str(x).zfill(6))

    # 종목코드로 시장구분 유추
    def infer_market(code):
        code_int = int(code)
        if code_int >= 100000:
            return "KOSDAQ"
        else:
            return "KOSPI"

    df['시장구분'] = df['종목코드'].apply(infer_market)
    return df

def save_stock_codes_to_json(df, save_path='data/stock_list.json'):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(df.to_dict(orient='records'), f, ensure_ascii=False, indent=2)
    print(f"✅ 저장 완료: {save_path}")

if __name__ == "__main__":
    df = get_all_stock_codes()
    save_stock_codes_to_json(df)