import sys
import os
# bigcontest_genAI 디렉토리를 Python 모듈 경로에 추가
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from utils.config import config  # config.yaml에서 경로와 설정을 가져옴
import pandas as pd
import re

def filter_fixed_address_purpose(input_address, purpose_choice, data):
    """
    방문 지역과 방문 목적에 따라 레스토랑을 필터링하고 반환하는 함수.
    
    [Parameters]:
    input_address (str)- 사용자가 입력한 지역 정보 리스트 (예: ['제주시 애월읍','서귀포시 남원읍']).
    purpose_choice (str)- 사용자가 선택한 목적 (예: '선택 안함', '식사', '카페/디저트').
    df- 필터링 적용할 데이터프레임

    [Returns]:
    pd.DataFrame: 필터링된 레스토랑 정보가 포함된 DataFrame.
    """
    print(f'고정질문: {input_address}, {purpose_choice}')
    print(f'입력 데이터 : {data.head(1)}')

    # Step 1: 지역 기반 필터링 
    # 지역을 선택하지 않았을 경우 필터링 하지 않은 데이터를 변수에 넣고, 선택했을 경우 선택한 모든 지역을 필터링하여 변수에 넣음
    if input_address == []:
        print('지역 선택 안함')
        filtered_by_address = data
    else:
        filtered_by_address = data[data['address_map'].apply(lambda x: isinstance(x, str) and any(addr in x for addr in input_address))]
        print(f'지역 필터링 완료, 길이:{len(filtered_by_address)}')
        print(f'지역 필터링 결과: {filtered_by_address["address_map"].unique()}')
    
    # Step 2: 목적에 따른 필터링 (상관 없음, 식사, 카페/디저트)
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

def filter_fixed_datetime_members(date, time, members, user_input):
    """
    방문 요일, 시간, 인원수에 따라 faiss검색 시 다른 키워드가 추가되도록 하는 함수.

    [Parameters]:
    date - 방문 요일 (월요일~일요일, 선택 안함)
    time - 방문 시간대 (아침, 점심, 저녁, 밤, 선택 안함)
    members - 방문 인원 (혼자, 2명~4명이상, 선택 안함)

    [Returns]:
    prompt - 사용자가 입력한 질문에 방문요일, 시간, 인원수에 따라 다른 키워드를 추가한 문자열.
    """
    # 인원수가 4명 이상인 경우 faiss 검색에 "예약가능"이 포함되도록 함
    if members == "4명 이상":
        prompt = user_input + f"{date} {time} 예약 가능"
    # 인원수가 혼자인 경우 faiss 검색에 "혼자"가 포함되도록 함
    elif members == "혼자": 
        prompt = user_input + f"{date} {time} 혼자"
    else:
        prompt = user_input + f"{date} {time}"
    return prompt

# 사용 예시
if __name__ == "__main__":
    # 사용자 입력 예시
    input_address = '제주시 (제주특별자치도 북부)'  # 사용자가 입력한 지역 정보
    purpose_choice = '식사'  # 목적 선택 (예: '상관없음', '식사', '카페/디저트')
    
    # 수정된 파일 경로
    categorized_data_file = '../data/categorized_restaurants.csv'  # 업로드된 경로 사용
    output_filename = 'map_purpose_filtered_example.csv'  # 결과를 저장할 파일 이름

    # 레스토랑 필터링 및 추천
    filtered_recommendations = filter_fixed_address_purpose(input_address, purpose_choice, categorized_data_file, output_filename)

    if filtered_recommendations is not None:
        print(f"Recommended restaurants saved to {output_filename}")
