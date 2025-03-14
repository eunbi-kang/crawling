from sentence_transformers import util
import numpy as np
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from konlpy.tag import Mecab
import re

# ✅ MongoDB 연결
MONGO_URI = "mongodb://eunbikang:1234@localhost:27017/admin"
client = MongoClient(MONGO_URI)
db = client["admin"]
collection = db["latest_news"]

# ✅ 한국어 SBERT 모델 (768차원)
model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS")

# ✅ Mecab 형태소 분석기 로드
mecab = Mecab()

# ✅ 형태소 분석 키워드 추출 (🔥 중복 제거 추가)
def extract_keywords(title, summary):
    title_keywords = mecab.nouns(title) if title else []
    summary_keywords = mecab.nouns(summary) if summary else []
    keywords = list(set(title_keywords + summary_keywords))  # ✅ 중복 제거

    if len(keywords) < 5:
        return (title + " " + summary).strip()
    return " ".join(keywords)

# ✅ **BM25 또는 문자열 포함 점수 계산 함수**
def compute_text_match_score(query, text):
    query_terms = query.split()
    match_count = sum(1 for term in query_terms if re.search(term, text, re.IGNORECASE))  # ✅ 대소문자 무시 검색

    return match_count / len(query_terms) if query_terms else 0  # ✅ 0~1 사이 값 반환

# ✅ **유사도 기반 뉴스 검색 (🔥 SBERT 유사도 + 문자열 포함 점수)**
def search_news(query, top_n=5, similarity_threshold=0.5):  # ✅ 유사도 기준 완화
    query_keywords = extract_keywords(query, query)
    print(f"✅ 형태소 분석 후 키워드: {query_keywords}")

    query_vector = model.encode(query_keywords).astype(np.float32)
    news_list = list(collection.find({}))
    results = []

    for news in news_list:
        if "vector" in news and news["vector"]:
            news_vector = np.array(news["vector"], dtype=np.float32)
            similarity = util.cos_sim(query_vector, news_vector).item()
            similarity_percentage = round(similarity * 100, 2)

            # 🔥 문자열 포함 점수 계산
            text_match_score = compute_text_match_score(query, news["title"])
            combined_score = (0.5 * similarity_percentage) + (0.5 * text_match_score * 100)  # ✅ 가중치 조정

            print(f"🔍 '{query}' vs. '{news['title']}' 유사도: {similarity_percentage}% (텍스트 포함 점수: {text_match_score * 100:.2f}%) → 최종 점수: {combined_score:.2f}%")

            if combined_score >= similarity_threshold * 100:
                news["similarity"] = round(combined_score, 2)
                results.append(news)

    results = sorted(results, key=lambda x: x["similarity"], reverse=True)[:top_n]

    if not results and similarity_threshold > 0.4:
        print("\n⚠️ 유사도 0.5 이상 결과 없음 → 유사도 0.4로 재검색")
        return search_news(query, top_n, similarity_threshold=0.4)

    return results


# ✅ 실행 (🔥 키워드 + 부분 검색 포함)
query = "전세사고"
results = search_news(query)

# ✅ 결과 출력
if results:
    print(f"\n🔍 검색어 '{query}'에 대한 검색 결과:")
    for idx, news in enumerate(results, start=1):
        print(f"\n[{idx}] {news['title']}  (유사도: {news['similarity']}%)")
        print(f"📅 {news['date']}")
        print(f"🔗 {news['link']}")
        print(f"📝 {news['summary']}")
        print("-" * 80)
else:
    print(f"\n❌ 검색어 '{query}'에 대한 적절한 뉴스가 없습니다.")
