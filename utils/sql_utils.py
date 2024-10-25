import pandasql as ps
import pandas as pd
from utils.config import model, df

# Function to convert question to SQL
def convert_question_to_sql(type):
    
    sql_prompt= f"""
    너는 주어진 텍스트를 바탕으로 SQL query를 작성하는 모델이야. 
    다음 규칙을 따라 SQL query를 작성해줘:

    1. 숫자형 데이터 (예: 비중, 현지인이용비중)와 관련된 경우:
    - 높아야 하면 `DESC` 정렬, 낮아야 하면 `ASC` 정렬을 사용해. ORDER BY로 써줘.
    - 조건에 명시되지 않은 수치형 데이터는 필터링 없이 두어.

    2. 문자열 데이터 (예: 개설일자, 판매음식종류, 지역, 이용건수, 이용금액, 건당평균이용금액)와 관련된 경우:
    - 문자열이 특정 단어를 포함해야 할 때는 `LIKE`와 wildcard `%`를 사용해.
        예시: `판매음식종류` LIKE '%커피%' 또는 `지역` LIKE '%애월읍%' 또는 `이용금액` LIKE '%하위 10%'
    - 이용건수, 이용금액, 건당평균이용금액은 낮은지 높은지나 BETWEEN 확인하지말고 '상위 10' 혹은 '25~50' 같이 정확한 워딩을 LIKE를 써서 검색해. 만약 ~ 가 들어있다면 그냥 그거 그대로 넣어 BETWEEN 쓰지마.
    - 지역에서는 앞에 제주도가 붙으면 무시해

    3. 테이블 이름은 항상 backtick 없이 df로 사용해.
    4. 항상 시작은 SELECT *로 시작해.
    5. 칼럼명은 주어지는 것과 동일하게 한국어로 작성하고, 칼럼명은 띄어쓰기 없이 사용해.
    6. SQL 쿼리는 백틱(`)으로 감싸서 칼럼명을 사용해. 예: `판매음식종류`, `개설일자`.
    7. 쿼리에 대한 설명은 필요 없고, 결과로 오직 SQL 쿼리만 반환해줘.
    8. LIMIT과 BETWEEN 쓰지마.

    {type}
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
    
