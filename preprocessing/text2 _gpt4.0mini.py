import pandas as pd
from openai import OpenAI

# OpenAI API 키 설정 (실제 API 키를 입력하세요)
api_key = ''
client = OpenAI(api_key=api_key)

def extract_keywords_and_summary(restaurant_name, review_content):
    # 메시지 프롬프트 구성
    messages = [
        {"role": "system", "content": "당신은 제주도 식당 리뷰 분석 전문가입니다. 감정 분석과 토픽 분석을 통해 고객 리뷰에서 중요한 정보를 추출하는 것이 목표입니다."},
        {"role": "user", "content": (
            f"다음은 {restaurant_name}에 대한 리뷰입니다. 이 리뷰에서 각 카테고리에 맞는 15개의 주요 키워드를 간결하게 추출해 주세요. "
            "키워드는 짧고 명확하게 작성해 주세요. 각 항목당 하나의 키워드 또는 간단한 문구만 작성해 주세요."
            "\n\n카테고리는 다음과 같습니다:\n"
            "1. 분위기 (예: 편안함, 활기참)\n"
            "2. 동행 대상 (예: 가족, 친구)\n"
            "3. 음식 맛 (예: 풍미, 신선함)\n"
            "4. 음식 양 (예: 적당, 과다)\n"
            "5. 서비스 (예: 친절함, 신속함)\n"
            "6. 가격 대비 만족도 (예: 가성비 좋음, 비쌈)\n"
            "7. 위생 상태 (예: 청결함, 불결함)\n"
            "8. 주차 및 접근성 (예: 주차 편리, 불편)\n"
            "9. 재방문 의향 (예: 재방문 의사 있음, 없음)\n"
            "10. 인기 메뉴 (예: 추천 요리 이름)\n"
            "11. 음료 및 디저트 (예: 음료 품질, 디저트 종류)\n"
            "12. 가족/아이 친화성 (예: 가족 친화적, 비친화적)\n"
            "13. 기념일에 적합한 장소 (예: 적합함, 부적합함)\n"
            "14. 혼잡도 (예: 붐빔, 한적함)\n"
            "15. 종합 평가 (예: 만족도 높음, 불만족)\n"
            f"\n리뷰 내용: {review_content}\n\n"
            "각 카테고리에 대해 해당 리뷰에서 추출한 키워드 또는 간단한 문구를 적어주세요. 구체적인 정보가 없는 경우, '해당 없음'으로 표시해 주세요."
        )}
    ]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages= messages,
        max_tokens=5000,
        temperature=0.5
    )
    
    keywords = response.choices[0].message.content.strip()
    return keywords   

# 리뷰 데이터 불러오기
# 예를 들어, 파일로부터 리뷰 데이터를 불러오는 경우
reviews_data = pd.read_csv('/Users/BigCon/data/restaurant_info_data_final.csv').reset_index()
reviews_data.drop(['index', 'Unnamed: 0'], axis=1, inplace=True)
for idx, review in enumerate(reviews_data['all_reviews']):
    if idx % 100 == 0:
        print(f'{idx}번째 인덱스까지 성공!')
    reviews_data.loc[idx, 'keyword'] = extract_keywords_and_summary(reviews_data['restaurant_name'][idx], review)


reviews_data.to_csv('restaurant_info_data_keyword_9000.csv', index=False)


# 식당 정보 요약 함수
def summarize_restaurant_data(row):
    restaurant_name = row['restaurant_name']
    
    # 식당의 기본 정보 텍스트 생성
    basic_info = (
        f"{restaurant_name}은(는) {row['category']} 카테고리에 속하는 식당입니다. "
        f"영업시간은 {row['business_hours']}이며, 주요 태그는 {row['tags']}입니다. "
        f"식당 정보로는 '{row['restaurant_info']}'가 있으며, 시설 정보로는 {row['restaurant_facility']}가 있습니다. "
        f"식당 소개는 '{row['restaurant_introduction']}'로 요약할 수 있습니다. "
        f"총 {row['total_reviews']}개의 리뷰가 있으며, 전체 평점은 {row['overall_rating']}입니다. "
        f"주요 메뉴 정보는 '{row['menu_info']}'입니다."
    )
    
    return basic_info

csv_file_path = '/Users/BigCon/data/restaurant_info_data_with_keyword.csv'
df = pd.read_csv(csv_file_path)

# 각 레스토랑에 대해 요약과 키워드를 추출하고 파일에 저장
for index, row in df.iterrows():
    restaurant_name = row['restaurant_name']
    review_content = row['all_reviews']
    
    # 리뷰가 없는 경우는 건너뛰기
    if pd.isna(review_content) or review_content.strip() == "" or review_content == '정보 없음':
        df.loc[index, 'keyword'] = f"{restaurant_name}에 리뷰가 없어 요약 및 키워드 추출을 생략합니다.\n\n"
    
    # 식당 정보 요약
    restaurant_info = df[df['restaurant_name'] == restaurant_name].iloc[0]
    basic_info = summarize_restaurant_data(restaurant_info)
    
    # 주요 키워드와 요약 추출
    summary = row['keyword']
    
    # 파일에 저장
    df.loc[index, 'text2'] = f"'{restaurant_name}'의 요약 및 주요 키워드:\n{basic_info}\n\n{summary}\n"
    
df.head()