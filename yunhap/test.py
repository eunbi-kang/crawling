import torch
import numpy as np
from pymongo import MongoClient
from transformers import AutoModel, AutoTokenizer
from sentence_transformers import util

# ✅ MongoDB 연결
MONGO_URI = "mongodb://eunbikang:1234@localhost:27017/admin"
client = MongoClient(MONGO_URI)
db = client["admin"]
collection = db["latest_news"]

# ✅ KoBigBird 모델 로드
MODEL_NAME = "monologg/kobigbird-bert-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

# ✅ 벡터 생성 함수 (float32로 변환 추가)
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

    embedding = output.last_hidden_state.mean(dim=1).squeeze().numpy()
    return embedding.astype(np.float32) / np.linalg.norm(embedding)  # 🔥 정규화 후 float32 변환

# ✅ 저장된 벡터 vs. 새로 생성한 벡터 비교
def compare_vectors():
    news_item = collection.find_one({"title": "전세사기 피해자 지원 정책 발표"})  # ✅ 저장된 뉴스 검색

    if not news_item:
        print("❌ 뉴스 데이터 없음")
        return

    stored_vector = np.array(news_item["vector"], dtype=np.float32)  # ✅ float32로 변환 후 저장된 벡터 불러오기
    new_vector = get_embedding(news_item["title"] + " " + news_item["summary"])  # ✅ 새로 생성한 벡터

    # ✅ 코사인 유사도 계산 (데이터 타입 통일)
    similarity = util.cos_sim(torch.tensor(stored_vector, dtype=torch.float32),
                              torch.tensor(new_vector, dtype=torch.float32)).item()

    print("\n✅ **벡터 비교 결과**")
    print(f"🔹 저장된 벡터 길이: {len(stored_vector)}")
    print(f"🔹 새로 생성한 벡터 길이: {len(new_vector)}")
    print(f"🔹 코사인 유사도: {similarity:.4f}")

    # ✅ 임계값 설정 (0.99 이상이면 동일하다고 판단)
    if similarity >= 0.99:
        print("✅ 저장된 벡터와 새로 생성한 벡터가 동일함!")
    else:
        print("⚠️ 벡터가 다름! → 저장 과정에서 문제 발생 가능성 있음.")

# ✅ 실행
compare_vectors()
