import json
import time

# ✅ 테스트용: 파일 불러오기
with open("data/post_app.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# ✅ 뉴스 리스트 추출
news_items = raw_data["Result"][0]

# ✅ 종목 정보 (예시)
stock_name = "자이언트스텝"
stock_code = "289220"
market = "KOSDAQ"

# ✅ 정제된 리스트로 가공
cleaned_news = []
for item in news_items:
    media_name = item.get("MediaName", "")

    if not media_name:
        print(f"⚠️ 언론사 없음: {item.get('Title', '')[:30]}...")

    cleaned_news.append({
        "종목명": stock_name,
        "종목코드": stock_code,
        "시장구분": market,
        "날짜": item.get("PublishDT", "unknown"),
        "제목": item.get("Title", ""),
        "url": item.get("Url", ""),
        "요약": item.get("Summary", ""),
        "언론사": media_name,
        "감성라벨": "unknown"
    })

# ✅ 저장 전 약간의 딜레이 (예: 파일 I/O 전 서버 안정용)
time.sleep(0.5)

# ✅ 결과 저장
with open("data/finup_news_cleaned.json", "w", encoding="utf-8") as f:
    json.dump(cleaned_news, f, ensure_ascii=False, indent=2)

print("✅ 저장 완료: data/finup_news_cleaned.json")
