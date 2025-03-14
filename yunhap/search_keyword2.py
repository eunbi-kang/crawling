from sentence_transformers import util
import numpy as np
from pymongo import MongoClient
from transformers import AutoModel, AutoTokenizer
from konlpy.tag import Mecab
import torch
import re

# ✅ MongoDB 연결
MONGO_URI = "mongodb://eunbikang:1234@localhost:27017/admin"
client = MongoClient(MONGO_URI)
db = client["admin"]
collection = db["latest_news"]

# ✅ KoBigBird 모델 로드
MODEL_NAME = "monologg/kobigbird-bert-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

# ✅ Mecab 형태소 분석기 로드
mecab = Mecab()

# ✅ **KoBigBird 임베딩 생성 함수 (Mean Pooling 적용)**
def get_embedding(text):
    tokens = tokenizer(
        text,
        padding=True,
        truncation=True,
        return_tensors="pt",
        max_length=512
    )
    with torch.no_grad():
        output = model(**tokens)

    # ✅ Mean Pooling 방식 적용
    embedding = output.last_hidden_state.mean(dim=1).squeeze().numpy()
    return embedding / np.linalg.norm(embedding)  # ✅ 벡터 정규화


# ✅ **형태소 분석 후 키워드 추출 (최소 10개 단어 유지)**
def extract_keywords(title, summary):
    # ✅ 제목과 요약에서 명사 추출
    title_keywords = mecab.nouns(title) if title else []
    summary_keywords = mecab.nouns(summary) if summary else []

    # ✅ 복합 명사 처리
    combined_text = title + " " + summary
    compound_keywords = mecab.nouns(combined_text)  # 전체 문장에서 명사 추출
    keywords = list(set(title_keywords + summary_keywords + compound_keywords))  # ✅ 중복 제거

    # ✅ 원본 검색어가 복합 명사일 경우 추가
    if " " not in combined_text.strip():  # 예: "전세사고"처럼 띄어쓰기 없는 경우
        keywords.append(combined_text.strip())

    # ✅ 최소 10개 단어 유지
    if len(keywords) < 10:
        keywords += combined_text.split()

    keywords = list(set(keywords))  # 최종 중복 제거
    return " ".join(keywords)


# ✅ **텍스트 포함 점수 계산 (제목 70% + 요약 30%)**
def compute_text_match_score(query, title, summary):
    query_terms = mecab.nouns(query)  # ✅ 형태소 분석으로 키워드 추출

    # 🔹 제목에서의 단어 포함 여부 계산 (가중치 0.7)
    title_match_count = sum(1 for term in query_terms if re.search(rf"\b{term}\b", title, re.IGNORECASE))
    title_score = (title_match_count / len(query_terms)) if query_terms else 0

    # 🔹 요약에서의 단어 포함 여부 계산 (가중치 0.3)
    summary_match_count = sum(1 for term in query_terms if re.search(rf"\b{term}\b", summary, re.IGNORECASE))
    summary_score = (summary_match_count / len(query_terms)) if query_terms else 0

    # ✅ 최종 텍스트 포함 점수 = 제목(70%) + 요약(30%)
    final_score = (title_score * 0.7) + (summary_score * 0.3)

    print(f"✅ 텍스트 포함 점수 계산: query_terms={query_terms}, title_match_count={title_match_count}, summary_match_count={summary_match_count}, final_score={final_score:.2%}")
    return final_score  # ✅ 0~1 사이 값 반환


# ✅ **유사도 기반 뉴스 검색 (KoBigBird + BM25 최적화)**
def search_news(query, top_n=5, similarity_threshold=0.4):
    query_keywords = extract_keywords(query, query)
    print(f"✅ 형태소 분석 후 키워드: {query_keywords.split()}")  # 리스트 형태로 출력

    query_vector = get_embedding(query_keywords)  # ✅ KoBigBird로 벡터화
    print(f"✅ 쿼리 벡터 길이: {len(query_vector)}")
    print(f"📊 쿼리 벡터 샘플: {query_vector[:5]}")  # 앞 5개 값 출력

    news_list = list(collection.find({}))
    results = []

    for news in news_list:
        if "vector" in news and news["vector"]:
            news_vector = np.array(news["vector"], dtype=np.float32)
            similarity = util.cos_sim(torch.tensor(query_vector, dtype=torch.float32),
                                      torch.tensor(news_vector, dtype=torch.float32)).item()
            similarity_percentage = round(similarity * 100, 2)

            # ✅ 텍스트 포함 점수 계산 (title + summary)
            text_match_score = compute_text_match_score(query, news["title"], news.get("summary", ""))

            # ✅ 최종 점수 = 벡터 유사도(60%) + 텍스트 포함 점수(40%)
            combined_score = (0.6 * similarity_percentage) + (0.4 * text_match_score * 100)

            print(f"🔍 '{query}' vs. '{news['title']}' 유사도: {similarity_percentage}% (텍스트 포함 점수: {text_match_score * 100:.2f}%) → 최종 점수: {combined_score:.2f}%")

            if combined_score >= similarity_threshold * 100:
                news["similarity"] = round(combined_score, 2)
                results.append(news)

    results = sorted(results, key=lambda x: x["similarity"], reverse=True)[:top_n]

    # ✅ 유사도 0.4 이상 결과 없을 경우 0.3으로 재검색
    if not results and similarity_threshold > 0.3:
        print("\n⚠️ 유사도 0.4 이상 결과 없음 → 유사도 0.3으로 재검색")
        return search_news(query, top_n, similarity_threshold=0.3)

    return results


# ✅ 실행 (KoBigBird 기반 검색 최적화)
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
