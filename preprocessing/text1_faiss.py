import faiss
import numpy as np
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModel

# Google Colab에서 GPU를 사용하도록 설정
device = "cuda" if torch.cuda.is_available() else "cpu"

# Hugging Face의 사전 학습된 임베딩 모델과 토크나이저 로드
model_name = "jhgan/ko-sroberta-multitask"
tokenizer = AutoTokenizer.from_pretrained(model_name)
embedding_model = AutoModel.from_pretrained(model_name).to(device)

# FAISS 인덱스 빌드 함수
def build_faiss_index(restaurant_descriptions):
    embeddings = []
    for desc in restaurant_descriptions:
        inputs = tokenizer(desc, return_tensors='pt', padding=True, truncation=True, max_length=512).to(device)
        with torch.no_grad():
            outputs = embedding_model(**inputs)
        embeddings.append(outputs.last_hidden_state.mean(dim=1).cpu().squeeze().numpy())

    embeddings = np.array(embeddings).astype('float32')

    # FAISS index 생성 및 학습
    dimension = embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(embeddings)

    return faiss_index, embeddings



# CSV 파일 로드 및 인덱스 생성
file_path = "/root/BigCon_genAI/data/modified_shinhancard_data_with_text.csv"  # Google Colab에 업로드한 경로
restaurant_data = pd.read_csv(file_path, usecols=['가맹점명', 'text'])
print(restaurant_data.head())

# FAISS 인덱스 빌드
faiss_index, embeddings = build_faiss_index(restaurant_data['text'].fillna("정보 없음").tolist())

# FAISS 인덱스 저장
faiss.write_index(faiss_index, '/root/BigCon_genAI/modules/modified_updated_text1_restaurant_faiss.index')
np.save('/root/BigCon_genAI/modules/modified_updated_text1_restaurant_embeddings.npy', embeddings)

print("FAISS 인덱스가 성공적으로 생성 및 저장되었습니다.")
