import torch
import faiss
import numpy as np
from transformers import AutoTokenizer, AutoModel
from utils.config import model, tokenizer, embedding_model, device

def text2faiss(user_input, embeddings_path, df):
    """

    [Parameters]:
    user_input - 사용자가 입력한 input
    embeddings_path -
    df - 고정질문을 통해 필터링된 데이터프레임

    [Returns]:
    top_300_restaurants : 사용자 입력과 유사한 상위 300개의 레스토랑 반환

    """

    # FAISS 임베딩 불러오기
    #faiss_index = faiss.read_index(faiss_index_path)
    embeddings = np.load(embeddings_path)

    # 필터링된 데이터의 인덱스 추출
    filtered_indices = df.index.tolist()
    # 필터링된 임베딩 추출
    filtered_embeddings = embeddings[filtered_indices]
    
    # FAISS 인덱스 빌드
    dimension = filtered_embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(filtered_embeddings)

    # 사용자 입력을 임베딩으로 변환
    inputs = tokenizer(user_input, return_tensors='pt', padding=True, truncation=True, max_length=512).to(device)
    with torch.no_grad():
        user_embedding = embedding_model(**inputs).last_hidden_state.mean(dim=1).cpu().squeeze().numpy().astype('float32')

    # FAISS로 유사한 식당 15개 추출, 필터링된 데이터가 15개보다 적을 경우 그만큼 추출
    search_count = min(15, len(df))
    distances, indices = faiss_index.search(np.array([user_embedding]), search_count)
    top_15_restaurants = df.iloc[indices[0]]
    
    return top_15_restaurants

def recommend_restaurant_from_subset(user_input, top_300_restaurants):
    # 전체 식당 설명을 한 번에 생성 (레스토랑 이름과 요약 정보를 사용)
    all_descriptions = "\n\n".join(
        [
            f"{restaurant['restaurant_name']}/ {restaurant['text2']} (영업 시간: {restaurant['business_hours']})"
            for idx, restaurant in top_300_restaurants.iterrows()
        ]
    )

    # Gemini 모델을 위한 메시지 구성
    print(f"description 길이: {len(all_descriptions)}")
    #messages = f"너는 사용자의 취향과 감정을 기반으로 제주도 맛집을 추천하는 챗봇이야. 사용자에게 맞는 식당을 대화하는 방식으로 추천해줘.{all_descriptions}는 식당 이름과 해당 식당에 대한 정보가 들어있는 데이터프래임이야. 사용자가 '{user_input}'라고 말했을 때 이 데이터프래임을 참고해서, 여기 있는 식당들을 다 둘러보고, 그 중에서 어떤 식당을 추천할지 3개를 골라주고, 그 이유를 설명해줘. 추천 식당은 최대한 겹치지 않게 해줘. 추천할만한 식당이 없다고 생각해도 꼭 하나는 추천해줘야해."
    messages = f"너는 사용자의 취향과 감정을 기반으로 제주도 맛집을 추천하는 챗봇이야. {all_descriptions}는 각 식당의 이름과 정보를 포함한 데이터프레임이야. 사용자가 '{user_input}'이라고 요청했을 때, 이 데이터프레임에 있는 식당들만 검토하고, 그 중에서 추천할 식당 3곳을 골라줘. 각 식당을 추천하는 이유도 설명해줘. 추천 식당은 서로 겹치지 않도록 해줘."

    print(f'messages = {messages}')
    print(user_input)
    print(len(all_descriptions))
    print("all_descriptions", model.count_tokens(all_descriptions))
    print("user_input_tokens: ", model.count_tokens(user_input))
    print("total_tokens: ", model.count_tokens(messages))

    # Gemini 1.5 Flash로 응답 생성
    response = model.generate_content(messages)
    response_text = response.text.strip()

    return response_text