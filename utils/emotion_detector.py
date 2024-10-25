from utils.config import model

def detect_emotion_and_context(question):
    """
    Detects whether the given question refers to specific elements related to restaurant data.
    If the question covers all the predefined items, it returns '1', otherwise, it returns '2'.

    Parameters:
    - question (str): The input question to analyze.
    - model (GenerativeModel): The pre-configured Generative AI model.

    Returns:
    - type (str): '1' if the question refers to all the predefined items, '2' otherwise.
    """

    
    prompt = f"""
    '{question}' 이 질문이 묻는 항목이 다음 리스트에 모두 포함되어있으면 1, 리스트에 포함되어 있지 않는 항목을 묻고있으면 2를 출력해주세요.
    [개설일자, 판매음식종류, 지역(_시 _동), 이용건수(상위 _%), 이용금액(상위 _%), 건당평균이용금액(상위 _%),
    월요일이용건수비중,화요일이용건수비중,수요일이용건수비중,목요일이용건수비중,금요일이용건수비중,토요일이용건수비중,일요일이용건수비중,
    5시부터11시이용건수비중,12시부터13시이용건수비중,14시부터17시이용건수비중,18시부터22시이용건수비중,23시부터4시이용건수비중,
    현지인이용비중,남성고객수비중,여성고객수비중,20대이하고객수비중,30대고객수비중,40대고객수비중,50대고객수비중,60대이상고객수비중] 
    """
    response = model.generate_content(prompt)

    if hasattr(response, 'candidates') and response.candidates:
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, 'text'):
                    type=part.text
    
    return type# 감정과 상황을 텍스트로 리턴