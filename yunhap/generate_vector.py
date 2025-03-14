from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
from konlpy.tag import Mecab

# ✅ MongoDB 연결
MONGO_URI = "mongodb://eunbikang:1234@localhost:27017/admin"
client = MongoClient(MONGO_URI)
db = client["admin"]
collection = db["latest_news"]

# ✅ 새로운 한국어 SBERT 모델 (768차원) 사용
model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS")

# ✅ 형태소 분석기 로드
mecab = Mecab()

print('---------------------------------------')



# ✅ 벡터 데이터 확인
news_list = list(collection.find({}))

print("\n✅ MongoDB 벡터 저장 확인")
for news in news_list[:5]:  # 상위 5개만 출력
    print(f"📰 제목: {news['title']}")
    if "vector" in news and news["vector"]:
        print(f"✅ 벡터 길이: {len(news['vector'])}")
        print(f"📊 벡터 샘플: {news['vector'][:5]} ...")  # 일부만 출력
    else:
        print("❌ 벡터 없음!")
    print("-" * 50)





exit()


# ✅ 형태소 분석을 이용한 키워드 추출 (title + summary 사용)
def extract_keywords(title, summary):
    title_keywords = mecab.nouns(title) if title else []
    summary_keywords = mecab.nouns(summary) if summary else []
    keywords = title_keywords + summary_keywords
    if len(keywords) < 3:
        return title + " " + summary if title and summary else summary
    return " ".join(keywords)


# ✅ 벡터 업데이트 함수 (새 모델로 벡터 다시 생성)
def update_news_vectors():
    news_list = list(collection.find({}, {"_id": 1, "title": 1, "summary": 1}))  # ✅ 필요한 필드만 조회

    for news in news_list:
        title = news.get("title", "")
        summary = news.get("summary", "")
        keywords = extract_keywords(title, summary)  # 🔥 형태소 분석 후 키워드 추출
        new_vector = model.encode(keywords).tolist()  # 🔥 새로운 모델로 벡터화

        # ✅ `vector` 필드만 업데이트, 기존 `id`, `img_url`, `date`는 그대로 유지됨
        collection.update_one({"_id": news["_id"]}, {"$set": {"vector": new_vector}})

    print("✅ 모든 뉴스 벡터를 새로운 모델로 업데이트 완료!")


# ✅ 실행
if __name__ == "__main__":
    update_news_vectors()
    print("🚀 벡터 업데이트 완료! 이제 검색 실행 가능.")
