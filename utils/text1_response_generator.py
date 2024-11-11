import re
import faiss
import torch
from utils.faiss_utils import load_faiss_index
from utils.config import model, config

# Multi-turn 대화 컨텍스트 관리
multi_turn_context = []

# 취소선 및 볼드 문법 제거 함수
def clean_text(text):
    # ~~취소선~~ 문법 제거
    text = re.sub(r"~~(.*?)~~", r"\1", text)
    # ~취소선~ 문법 제거
    text = re.sub(r"~(.*?)~", r"\1", text)
    # **"텍스트"**를 <b>"텍스트"</b>로 변환
    text = re.sub(r'\*\*"(.*?)"\*\*', r'<b>"\1"</b>', text)
    # **텍스트**를 <b>텍스트</b>로 변환
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    return text

# Main function to generate response using FAISS and Gemini
def generate_response_with_faiss(question, df, embeddings, model, embed_text, k=3):
    index_path = config['faiss']['faiss_index']
    print(index_path)

    # Load FAISS index
    # index = load_faiss_index(index_path)

    # 필터링된 데이터의 인덱스 추출
    filtered_indices = df.index.tolist()

    # 추출된 인덱스를 통해 임베딩 데이터에서 필터링된 데이터만 추출
    filtered_embeddings = embeddings[filtered_indices]

    # Query embedding
    query_embedding = embed_text(question).reshape(1, -1)

    # FAISS 인덱스 빌드
    dimension = filtered_embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(filtered_embeddings)

    # 가장 유사한 텍스트 검색 (3배수)
    distances, indices = faiss_index.search(query_embedding, k * 3)

    # FAISS로 검색된 상위 k개의 데이터프레임 추출
    filtered_df = df.iloc[indices[0, :]].copy().reset_index(drop=True)

    reference_info = ""
    for idx, row in filtered_df.iterrows():
        reference_info += f"{row['text']}\n"

    # 대화 히스토리를 포함한 프롬프트 구성
    conversation_history = "\n".join(multi_turn_context)
    prompt = f"{conversation_history}\n질문: {question}\n참고할 정보:\n{reference_info}\n응답은 친절하게 추천하는 챗봇처럼:"

    print(model.count_tokens(prompt))
    try:
        response = model.generate_content(prompt)
        # Print the response text in the terminal
        if response._result and response._result.candidates:
            generated_text = response._result.candidates[0].content.parts[0].text
            # 취소선 및 볼드 문법 제거
            generated_text = clean_text(generated_text)

        else:
            generated_text = "죄송해요. 추천에 필요한 정보가 조금 부족한 것 같아요🥲 구체적으로 다시 질문해주시면 그에 딱 맞는 멋진 곳을 추천해 드릴게요!🥰"
            print("No valid response generated.")

        # 대화 컨텍스트에 질문과 응답 추가
        multi_turn_context.append(f"질문: {question}")
        multi_turn_context.append(f"응답: {generated_text}")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        generated_text = "죄송해요. 추천에 필요한 정보가 조금 부족한 것 같아요🥲 구체적으로 다시 질문해주시면 그에 딱 맞는 멋진 곳을 추천해 드릴게요!🥰"

    return generated_text

# Function to generate response based on SQL query results
def generate_gemini_response_from_results(sql_results, question):
    if sql_results.empty:
        return "죄송해요. 추천에 필요한 정보가 조금 부족한 것 같아요🥲 구체적으로 다시 질문해주시면 그에 딱 맞는 멋진 곳을 추천해 드릴게요!🥰"

    best_match = sql_results.iloc[:3]
    print(best_match)
    reference_info = ""
    for idx, row in best_match.iterrows():
        reference_info += f"{row['text']}\n"

    conversation_history = "\n".join(multi_turn_context)
    prompt = f"{conversation_history}\n질문: {question}\n참고할 정보:\n{reference_info}\n응답은 최대한 친절하고 친근하게 식당 추천해주는 챗봇처럼:"
    print("input_tokens: ", model.count_tokens(prompt))
    print("sql_참고자료 tokens: ", model.count_tokens(reference_info))

    try:
        response = model.generate_content(prompt)
        if hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if hasattr(part, 'text'):
                        response_text = part.text
                        # 취소선 제거
                        response_text = clean_text(response_text)
                        
        else:
            response_text = "죄송해요. 추천에 필요한 정보가 조금 부족한 것 같아요🥲 구체적으로 다시 질문해주시면 그에 딱 맞는 멋진 곳을 추천해 드릴게요!🥰"
        
        # 대화 컨텍스트에 질문과 응답 추가
        multi_turn_context.append(f"질문: {question}")
        multi_turn_context.append(f"응답: {response_text}")
    
    except Exception as e:
        print(f"Error occurred: {e}")
        response_text = "죄송해요. 추천에 필요한 정보가 조금 부족한 것 같아요🥲 구체적으로 다시 질문해주시면 그에 딱 맞는 멋진 곳을 추천해 드릴게요!🥰"

    return response_text
