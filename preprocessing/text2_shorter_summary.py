# 식당 정보 요약 함수
def summarize_restaurant_data(row):
    restaurant_name = row['restaurant_name']
    
    # 식당의 기본 정보 텍스트 생성
    basic_info = (
        f"{restaurant_name}의 카테고리: {row['category']}/ 식당정보:{row['restaurant_info']}/ 리뷰: {row['total_reviews']}개, 평점:{row['overall_rating']}점/ 키워드:{row['keyword']}"
    )
    
    return basic_info

csv_file_path = '/Users/minseo/BigCon/bigcontest_genAI/data/updated_final_kakao_restaurant_with_address_map_text2.csv'
df = pd.read_csv(csv_file_path)

# 각 레스토랑에 대해 요약과 키워드를 추출하고 파일에 저장
for index, row in df.iterrows():
    restaurant_name = row['restaurant_name']
    
    # 식당 정보 요약
    restaurant_info = df[df['restaurant_name'] == restaurant_name].iloc[0]
    basic_info = summarize_restaurant_data(restaurant_info).replace("\n"," ").replace(". ", ".")
    
    # 파일에 저장
    df.loc[index, 'text2'] = f'{basic_info}'
df.head()
df.to_csv('/Users/BigCon/bigcontest_genAI/data/updated_final_kakao_restaurant_with_address_map_text2.csv')