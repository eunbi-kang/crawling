# 📊 FinUp 뉴스 & 종목 데이터 크롤러  

KRX 상장 종목 리스트를 크롤링하고, 해당 종목의 뉴스를 FinUp API에서 가져오는 Python 프로젝트입니다.  

---

## 🏗 프로젝트 구조  
```bash
🗂finup
├── 📁 data
│   ├── finup_news_cleaned.json   # 크롤링된 뉴스 데이터
│   ├── stock_list.json           # 종목 리스트 (KOSPI, KOSDAQ, KONEX)
├── 📁 news_data                     # 추가적인 뉴스 데이터 저장 폴더
├── crawl_finup_news.py           # FinUp 뉴스 크롤링 코드
├── getAllStockCodes.py           # KRX 종목 리스트 크롤링 코드
```

---

## 🛠 기능  

### ✅ 1. 종목 리스트 수집 (`getAllStockCodes.py`)
- 한국거래소(KRX)에서 코스피, 코스닥, 코넥스 상장 종목 리스트를 가져옴
- 종목명, 종목코드, 시장구분 데이터를 `data/stock_list.json`에 저장  

### ✅ 2. 뉴스 크롤링 (`crawl_finup_news.py`)
- `stock_list.json`을 기반으로 FinUp API를 호출하여 뉴스 크롤링  
- 뉴스 제목, 날짜, 언론사, 요약을 포함한 JSON 파일 생성  
- 결과 저장: `data/finup_news_cleaned.json`  

---

## 🔧 실행 방법  

### 📌 1) 종목 리스트 크롤링  
```bash
python getAllStockCodes.py
```
→ `data/stock_list.json` 파일이 생성됨

### 📌 2) 뉴스 데이터 크롤링
```bash
python crawl_finup_news.py
```
→ `data/finup_news_cleaned.json` 파일이 생성됨

