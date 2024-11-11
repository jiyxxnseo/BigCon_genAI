import torch
import faiss
import numpy as np
from transformers import AutoTokenizer, AutoModel
from utils.config import model, tokenizer, embedding_model, device, config

# Multi-turn 대화 컨텍스트 관리
multi_turn_context = []

def text2faiss(user_input, df):
    """
    [Parameters]:
    user_input - 사용자가 입력한 input
    df - 고정질문을 통해 필터링된 데이터프레임

    [Returns]:
    top_15_restaurants - 사용자 입력과 유사한 상위 15개의 레스토랑 반환
    """
    # FAISS 임베딩 불러오기
    embeddings_path = config['faiss']['text2_embeddings']
    embeddings = np.load(embeddings_path)

    # 필터링된 데이터의 인덱스 추출
    filtered_indices = df.index.tolist()
    
    # 추출된 인덱스를 통해 임베딩 데이터에서 필터링된 데이터만 추출
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

def recommend_restaurant_from_subset(user_input, top_15_restaurants):
    """
    FAISS 검색으로 반환된 15개 레스토랑을 통해 gemini를 호출해 추천을 진행하는 함수. 에러가 나거나 결과가 없을 시 기본메세지 반환.

    [Parameters]:
    user_input - 사용자가 입력한 질문
    top_15_restaurants - FAISS를 통해 추출된 15개의 레스토랑 DataFrame
    
    [Returns]:
    response - Gemini의 응답 텍스트
    """
    all_descriptions = "\n\n".join(
        [f"{restaurant['restaurant_name']} / {restaurant['text2']} (영업 시간: {restaurant['business_hours']})"
         for _, restaurant in top_15_restaurants.iterrows()]
    )
    print(f"description 길이: {len(all_descriptions)}")

    # Multi-turn 대화를 위한 컨텍스트 사용
    conversation_history = "\n".join(multi_turn_context)
    # Gemini 모델을 위한 프롬프트 구성
    messages = f"{conversation_history}\n너는 사용자의 취향과 감정을 기반으로 제주도 맛집을 추천하는 챗봇이야. {all_descriptions}는 각 식당의 이름과 정보를 포함한 데이터프레임이야. 사용자가 '{user_input}'이라고 요청했을 때, 이 데이터프레임에 있는 식당들만 검토하고, 그 중에서 추천할 식당 3곳을 골라줘. 각 식당을 추천하는 이유도 설명해줘. 추천 식당은 서로 겹치지 않도록 해줘."

    print(f'messages = {messages}')
    print(user_input)
    print("all_descriptions", model.count_tokens(all_descriptions))
    print("user_input_tokens: ", model.count_tokens(user_input))
    print("total_tokens: ", model.count_tokens(messages))

    try:
        # Gemini 1.5 Flash로 응답 생성
        response = model.generate_content(messages)
        # response = response.text.strip()
        if hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if hasattr(part, 'text'):
                        response = part.text
        # 응답이 없을 경우 기본 메시지 설정
        else:
            response = "추천에 필요한 정보가 부족해요. 다시 구체적으로 질문해주세요!"

        # 대화 컨텍스트에 질문과 응답 추가
        multi_turn_context.append(f"질문: {user_input}")
        multi_turn_context.append(f"응답: {response}")

    except Exception as e:
        # 에러 발생 시 기본 메세지 반환
        print(f"Error occurred: {e}")
        response = "추천에 필요한 정보가 부족해요. 다시 구체적으로 질문해주세요!"

    return response