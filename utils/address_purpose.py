import sys
import os

# bigcontest_genAI 디렉토리를 Python 모듈 경로에 추가
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from utils.config import config  # config.yaml에서 경로와 설정을 가져옴
import pandas as pd
import re
def filter_and_recommend_restaurants(input_address, purpose_choice, data):
    """
    지역 정보와 목적에 따라 레스토랑을 필터링하고 CSV 파일로 저장하는 함수.
    
    Parameters:
    input_address (str): 사용자가 입력한 지역 정보 리스트 (예: ['제주시 애월읍','서귀포시 남원읍']).
    purpose_choice (str): 사용자가 선택한 목적 (예: '선택 안함', '식사', '카페/디저트').
    df : 필터링 적용할 데이터프레임

    Returns:
    pd.DataFrame: 필터링된 레스토랑 정보가 포함된 DataFrame.
    """
    print(f'입력인자: {input_address}, {purpose_choice}')
    print(f'입력 데이터 : {data.head(1)}')
    # Step 1: 지역 기반 필터링 

    if input_address == []:
        print('지역 선택 안함')
        filtered_by_address = data
    else:
        # filtered_by_address = data[data['address_map'].str.contains(input_address, case=False, na=False, regex=False)]
        filtered_by_address = data[data['address_map'].apply(lambda x: isinstance(x, str) and any(addr in x for addr in input_address))]
        print(f'지역 필터링 완료, 길이:{len(filtered_by_address)}')
        print(f'지역 필터링 결과: {filtered_by_address["address_map"].unique()}')
    
    # Step 2: 목적에 따른 필터링 (상관없음, 식사, 카페/디저트)
    categorized_restaurants_df = pd.read_csv(config['data']['categorized_data'])
    
    if purpose_choice == '선택 안함':
        # 지역 필터링만 한 데이터를 저장하고 반환
        print('방문목적 선택 안함')
        return filtered_by_address
    
    # 선택된 목적에 따른 카테고리 필터링
    filtered_categories = categorized_restaurants_df[categorized_restaurants_df['purpose'] == purpose_choice]['category'].values[0]
    
    # 정규 표현식을 사용하여 쉼표로 구분된 카테고리 추출 (쉼표가 포함된 경우도 포함)
    category_list = re.findall(r"'([^']*)'", filtered_categories)
    category_list = [cat.strip() for cat in category_list]
    
    # 카테고리가 매칭되는지 확인하는 함수 (쉼표 포함된 문자열을 전체로 비교)
    def category_match(restaurant_categories, category_list):
        restaurant_category = restaurant_categories.lower().strip()
        return any(restaurant_category == cat.lower().strip() for cat in category_list)
    
    # 카테고리를 기준으로 필터링
    final_filtered_data = filtered_by_address[filtered_by_address['category'].apply(lambda x: category_match(x, category_list))]
    print(f'방문목적 필터링 완료, 길이: {len(final_filtered_data)}')  
    print(f'방문목적 필터링 결과: {final_filtered_data["category"].unique()}')
    print(f'지역 필터링 결과: {final_filtered_data["address_map"].unique()}')
    return final_filtered_data

# 사용 예시
if __name__ == "__main__":
    # 사용자 입력 예시
    input_address = '제주시 (제주특별자치도 북부)'  # 사용자가 입력한 지역 정보
    purpose_choice = '식사'  # 목적 선택 (예: '상관없음', '식사', '카페/디저트')
    
    # 수정된 파일 경로
    categorized_data_file = '../data/categorized_restaurants.csv'  # 업로드된 경로 사용
    output_filename = 'map_purpose_filtered_example.csv'  # 결과를 저장할 파일 이름

    # 레스토랑 필터링 및 추천
    filtered_recommendations = filter_and_recommend_restaurants(input_address, purpose_choice, categorized_data_file, output_filename)

    if filtered_recommendations is not None:
        print(f"Recommended restaurants saved to {output_filename}")
