import pandasql as ps
import pandas as pd
from utils.config import model, df

# Function to convert question to SQL
def convert_question_to_sql(question):
    prompt = f"다음 질문에서 묻는 정보를 각 항목마다 항목이 높아야 되는지 낮아야되는지 카페나 지역같은 정확한 정보가 있는지 정리하세요.: {question} 질문이 묻는 정보가 아니라면 항목에 '해당없음'이라고 적어주세요.\n개설일자:,판매음식종류:['가정식', '단품요리 전문', '커피', '베이커리', '일식', '치킨', '중식', '분식', '햄버거', '양식', '맥주/요리주점', '아이스크림/빙수', '피자', '샌드위치/토스트', '차', '꼬치구이', '기타세계요리', '구내식당/푸드코트', '떡/한과', '도시락', '도너츠', '주스', '동남아/인도음식', '패밀리 레스토랑', '기사식당', '야식', '스테이크', '포장마차', '부페', '민속주점']중 하나,지역:(_시 _동),이용건수:(상위 _%),이용금액:(상위 _%), 건당평균이용금액:(상위 _%),월요일이용건수비중:,화요일이용건수비중:,수요일이용건수비중:,목요일이용건수비중:,금요일이용건수비중:,토요일이용건수비중:,일요일이용건수비중:,현지인이용비중:,20대이하고객수비중:,30대고객수비중:,40대고객수비중:,50대고객수비중:,60대이상고객수비중:"
    response = model.generate_content(prompt)

    if hasattr(response, 'candidates') and response.candidates:
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, 'text'):
                    response= part.text
    print(response)
    
    sql_prompt= f"""
    너는 주어진 텍스트를 바탕으로 SQL query를 작성하는 모델이야. 
    다음 규칙을 따라 SQL query를 작성해줘:

    1. 숫자형 데이터 (예: 비중, 건수)와 관련된 경우:
    - 높아야 하면 `DESC` 정렬, 낮아야 하면 `ASC` 정렬을 사용해.
    - 조건에 명시되지 않은 수치형 데이터는 필터링 없이 두어.

    2. 문자열 데이터 (예: 개설일자, 판매음식종류, 지역)와 관련된 경우:
    - 문자열이 특정 단어를 포함해야 할 때는 `LIKE`와 wildcard `%`를 사용해.
        예시: `판매음식종류` LIKE '%커피%' 또는 `지역` LIKE '%제주시 애월읍%'

    3. 테이블 이름은 항상 backtick 없이 df로 사용해.
    4. 항상 시작은 SELECT *로 시작해.
    5. 칼럼명은 주어지는 것과 동일하게 한국어로 작성하고, 칼럼명은 띄어쓰기 없이 사용해.
    6. SQL 쿼리는 백틱(`)으로 감싸서 칼럼명을 사용해. 예: `판매음식종류`, `개설일자`.
    7. 쿼리에 대한 설명은 필요 없고, 결과로 오직 SQL 쿼리만 반환해줘.
    8. LIMIT은 쓰지마.

    {response}
    """
    to_sql= model.generate_content(sql_prompt)
    # Extracting the SQL query from the response
    sql_query = to_sql.candidates[0].content.parts[0].text
    
    # Removing the ```sql and ``` markers
    sql_query_cleaned = sql_query.strip().strip("```sql").strip("```").strip()
    return sql_query_cleaned

# Function to execute SQL query on DataFrame using Pandas
def execute_sql_query_on_df(query, df):
    try:
        # Use pandasql to execute the query on the DataFrame
        result_df = ps.sqldf(query, locals())
        return result_df
    except Exception as e:
        print(f"Error executing query: {e}")
        return pd.DataFrame()
    
