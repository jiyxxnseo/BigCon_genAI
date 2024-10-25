from utils.faiss_utils import load_faiss_index
from utils.config import model, config


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



    prompt = f"질문: {question}\n참고할 정보:\n{reference_info}\n응답은 최대한 친절하게 식당 추천해주는 챗봇처럼:"
    
    response = model.generate_content(prompt)

    # Print the response text in the terminal
    if response._result and response._result.candidates:
        generated_text = response._result.candidates[0].content.parts[0].text
        #print(generated_text)  # Print the actual response
    else:
        print("No valid response generated.")
    
    return generated_text


# Function to generate response based on SQL query results
def generate_gemini_response_from_results(sql_results, question):
    if sql_results.empty:
        return "결과가 없습니다."
    
    # Extract key data from the best match (top result from SQL query)
    best_match = sql_results.iloc[:4]  # Assuming the first row is the best match

    reference_info = ""
    for idx, row in best_match.iterrows():
        reference_info += f"{row['text']}\n"


    prompt = f"질문: {question}\n참고할 정보:\n{reference_info}\n응답은 최대한 친절하고 친근하게 식당 추천해주는 챗봇처럼:"

    # Generate response using Gemini model
    response = model.generate_content(prompt)
    if hasattr(response, 'candidates') and response.candidates:
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, 'text'):
                    response=part.text
    return response