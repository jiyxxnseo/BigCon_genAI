import faiss
import os
import numpy as np
import torch
from utils.config import tokenizer, embedding_model, device

# Load FAISS index for text1
def load_faiss_index(index_path):
    if os.path.exists(index_path):
        index = faiss.read_index(index_path)
        print(f"FAISS index loaded from {index_path}.")
        return index
    else:
        raise FileNotFoundError(f"{index_path} file not found.")

# Embed text for text1 
def embed_text(text):
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True).to(device)
    with torch.no_grad():
        # 모델의 출력을 GPU에서 연산하고, 필요한 부분을 가져옴
        embeddings = embedding_model(**inputs).last_hidden_state.mean(dim=1)
    return embeddings.squeeze().cpu().numpy() # 결과를 CPU로 이동하고 numpy 배열로 변환


