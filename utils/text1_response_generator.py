from utils.faiss_utils import load_faiss_index
from utils.config import model, config

# Multi-turn 대화 컨텍스트 관리
multi_turn_context = []

# Main function to generate response using FAISS and Gemini
def generate_response_with_faiss(question, df, embeddings, model, embed_text, k=3):
    index_path = config['faiss']['faiss_index']
    print(index_path)

    # Load FAISS index
    index = load_faiss_index(index_path)

    # Query embedding
    query_embedding = embed_text(question).reshape(1, -1)

    # 가장 유사한 텍스트 검색 (3배수)
    distances, indices = index.search(query_embedding, k*3)

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
            #print(generated_text)  # Print the actual response
        else:
            # 응답이 없는 경우 기본 메세지 설정
            generated_text = "죄송해요. 추천에 필요한 정보가 조금 부족한 것 같아요🥲 구체적으로 다시 질문해주시면 그에 딱 맞는 멋진 곳을 추천해 드릴게요!🥰"
            print("No valid response generated.")

        # 대화 컨텍스트에 질문과 응답 추가
        multi_turn_context.append(f"질문: {question}")
        multi_turn_context.append(f"응답: {generated_text}")
        
    except Exception as e:
        # 에러가 발생하면 기본 메시지 반환
        print(f"Error occurred: {e}")
        generated_text = "죄송해요. 추천에 필요한 정보가 조금 부족한 것 같아요🥲 구체적으로 다시 질문해주시면 그에 딱 맞는 멋진 곳을 추천해 드릴게요!🥰"

    
    return generated_text


# Function to generate response based on SQL query results
def generate_gemini_response_from_results(sql_results, question):
    """
    SQL 쿼리를 통해 반환된 데이터에서 4개를 선택 후 gemini를 호출해 추천을 진행하는 함수. 에러가 나거나 결과가 없을 시 기본메세지 반환.

    [Parameters]:
    - sql_results (df) : SQL 쿼리를 통해 반환된 데이터
    - question (str) : 사용자가 입력한 질문

    [Returns]:
    response (str) : Gemini의 응답 텍스트
    """
    if sql_results.empty:
        return  "죄송해요. 추천에 필요한 정보가 조금 부족한 것 같아요🥲 구체적으로 다시 질문해주시면 그에 딱 맞는 멋진 곳을 추천해 드릴게요!🥰"

    # 데이터에서 상위 3개를 추출 (가장 첫 행이 Best Match라고 가정)
    best_match = sql_results.iloc[:3]
    print(best_match)
    reference_info = ""
    for idx, row in best_match.iterrows():
        reference_info += f"{row['text']}\n"

    prompt = f"질문: {question}\n참고할 정보:\n{reference_info}\n응답은 최대한 친절하고 친근하게 식당 추천해주는 챗봇처럼:"
    print("input_tokens: ", model.count_tokens(prompt))
    print("sql_참고자료 tokens: ", model.count_tokens(reference_info))

    try:
        # Generate response using Gemini model
        response = model.generate_content(prompt)
        if hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if hasattr(part, 'text'):
                        response=part.text
        else:
            # 응답이 없을 경우 기본 메세지 설정
            response = "죄송해요. 추천에 필요한 정보가 조금 부족한 것 같아요🥲 구체적으로 다시 질문해주시면 그에 딱 맞는 멋진 곳을 추천해 드릴게요!🥰"
    
    except Exception as e:
        # 에러 발생 시 기본 메세지 반환
        print(f"Error occurred: {e}")
        response = "죄송해요. 추천에 필요한 정보가 조금 부족한 것 같아요🥲 구체적으로 다시 질문해주시면 그에 딱 맞는 멋진 곳을 추천해 드릴게요!🥰"

    return response

