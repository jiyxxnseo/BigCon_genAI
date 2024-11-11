import pandas as pd
import re

def remove_gita_restaurants(data_file, categorized_data_file, output_filename):
    """
    '기타'에 해당하는 카테고리의 식당들을 제거하고 '기타'에 해당하는 카테고리 리스트와 해당 식당들을 출력하는 함수.
    
    Parameters:
    data_file (str): 레스토랑 데이터가 포함된 CSV 파일 경로 ('final_kakao_data_with_address_map_text2.csv').
    categorized_data_file (str): '기타' 목적에 해당하는 카테고리 데이터가 포함된 CSV 파일 경로 ('categorized_restaurants.csv').
    output_filename (str): 필터링된 결과를 저장할 CSV 파일명.
    
    Returns:
    pd.DataFrame: '기타' 카테고리의 식당들이 제거된 DataFrame.
    """
    # Step 1: 레스토랑 데이터 로드
    data = pd.read_csv(data_file)
    
    # Step 2: '기타'에 해당하는 카테고리 추출
    categorized_restaurants_df = pd.read_csv(categorized_data_file)
    filtered_categories = categorized_restaurants_df[categorized_restaurants_df['purpose'] == '기타']['category'].values
    
    # 정규 표현식을 사용하여 '로 묶인 항목을 추출 (쉼표 포함 처리)
    gita_category_list = []
    for category_str in filtered_categories:
        gita_category_list.extend(re.findall(r"'([^']*)'", category_str))  # '로 묶인 항목을 추출
    
    # 소문자로 변환하고 공백 제거
    gita_category_list = [cat.lower().strip() for cat in gita_category_list]
    
    # '기타' 카테고리 항목을 출력
    print("Categories under '기타':")
    for category in gita_category_list:
        print(f"- {category}")
    
    # Step 3: 카테고리가 매칭되는지 확인하는 함수
    def category_match(restaurant_category, category_list):
        # 레스토랑의 category 값을 그대로 비교 (쉼표 포함된 문자열을 하나의 항목으로 처리)
        restaurant_category = restaurant_category.lower().strip()
        
        # 매칭 여부 디버깅 출력
        print(f"\nChecking category: {restaurant_category}")
        
        # restaurant의 category가 기타 카테고리 리스트와 일치하면 True 반환
        match = restaurant_category in category_list
        print(f"Match found: {match}")
        return match
    
    # '기타' 카테고리에 속한 식당들을 추출
    gita_restaurants = data[data['category'].apply(lambda x: category_match(x, gita_category_list))]
    
    # '기타' 카테고리 식당 추출 결과 출력
    print(f"\nRestaurants in '기타' category (Total: {len(gita_restaurants)}):")
    if not gita_restaurants.empty:
        print(gita_restaurants[['restaurant_name_2', 'category']])  # 'restaurant_name_2'와 'category'를 출력
    
    # '기타' 카테고리에 속한 식당을 제거한 데이터
    filtered_data = data[~data['category'].apply(lambda x: category_match(x, gita_category_list))]
    
    # Step 4: 필터링된 데이터를 CSV 파일로 저장
    filtered_data.to_csv(output_filename, index=False)
    
    # 출력: 제거된 '기타' 카테고리 식당 수와 필터링 후 남은 식당 수
    print(f"\nTotal number of '기타' category restaurants removed: {len(gita_restaurants)}")
    print(f"Total number of restaurants after removing '기타' category: {len(filtered_data)}")
    
    return filtered_data

# 사용 예시
data_file = 'updated_full_combined_with_address_map.csv'  # 레스토랑 데이터 파일
categorized_data_file = 'categorized_restaurants.csv'  # 카테고리별 목적 데이터 파일
output_filename = 'final_kakao_restaurant_with_address_map_text2.csv'  # 결과를 저장할 파일 이름

# '기타' 카테고리 제거
filtered_restaurants = remove_gita_restaurants(data_file, categorized_data_file, output_filename)

if filtered_restaurants is not None:
    print(f"\nFiltered restaurants saved to {output_filename}")
