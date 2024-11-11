import pandas as pd

# 'address_2'에서 첫 세 단어를 추출하는 함수 정의
def extract_address_map(address):
    if isinstance(address, str):  # 값이 문자열인지 확인
        return ' '.join(address.split()[:3])
    else:
        return None  # 문자열이 아닌 값에 대해 None 반환

# 대괄호를 제거하되 레스토랑 이름 주위의 큰따옴표는 유지하는 함수 정의
def remove_square_brackets(df, column_name):
    # 대괄호를 제거하고 큰따옴표를 유지
    df[column_name] = df[column_name].apply(lambda x: x.replace("[", "").replace("]", "").replace("'", '"'))
    return df

# 원본 CSV 파일 불러오기
file_path = 'full_combined_restaurant_info_data_text2.csv'
df = pd.read_csv(file_path, index_col=0)

# 'address_2'에 함수를 적용하여 'address_map'이라는 새로운 컬럼 생성
df['address_map'] = df['address_2'].apply(extract_address_map)

# 컬럼 순서를 'address_2' 옆에 'address_map'을 배치하도록 재배열
columns = df.columns.tolist()
address_2_index = columns.index('address_2')
columns.insert(address_2_index + 1, columns.pop(columns.index('address_map')))
df = df[columns]

# 고유한 'address_map' 값의 개수 확인
unique_address_map_count = df['address_map'].nunique()

# 'address_map' 컬럼이 추가된 수정된 DataFrame 저장
output_file = 'full_combined_with_address_map.csv'
df.to_csv(output_file)

# 고유한 'address_map' 값의 개수 출력
print(f"Number of unique address_map values: {unique_address_map_count}")

# 'address_map' 컬럼이 포함된 수정된 CSV 파일 불러오기
df = pd.read_csv(output_file, index_col=0)

# 'address_map'을 기준으로 그룹화하고 'restaurant_name_2'를 리스트로 묶음
grouped_df = df.groupby('address_map')['restaurant_name_2'].apply(list).reset_index()

# 그룹화된 데이터를 새로운 CSV 파일로 저장
grouped_output_file = 'grouped_by_address_map_restaurant_names.csv'
grouped_df.to_csv(grouped_output_file, index=False)

print(f"Grouped data saved to: {grouped_output_file}")

# 그룹화된 CSV 파일 불러오기
df_grouped = pd.read_csv('grouped_by_address_map_restaurant_names.csv')

# 'restaurant_name_2' 컬럼의 대괄호를 제거하는 함수 적용
df_cleaned = remove_square_brackets(df_grouped, 'restaurant_name_2')

# 정리된 DataFrame을 다시 CSV 파일로 저장
cleaned_output_file = 'cleaned_grouped_by_address_map_restaurant_names.csv'
df_cleaned.to_csv(cleaned_output_file, index=False)

print("Data cleaned and saved successfully with quotes!")

# 제외할 읍면 리스트 정의
exclude_list = [
    "제주특별자치도 서귀포시 남원읍", "제주특별자치도 서귀포시 대정읍", "제주특별자치도 서귀포시 성산읍", 
    "제주특별자치도 서귀포시 안덕면", "제주특별자치도 서귀포시 표선면", 
    "제주특별자치도 제주시 구좌읍", "제주특별자치도 제주시 애월읍", "제주특별자치도 제주시 우도면", 
    "제주특별자치도 제주시 조천읍", "제주특별자치도 제주시 한경면", "제주특별자치도 제주시 한림읍", "제주특별자치도 제주시 추자면"
]

# "제주특별자치도 서귀포시"로 시작하는 row 묶기
seogwipo_rows = df_cleaned[df_cleaned['address_map'].str.startswith("제주특별자치도 서귀포시")]
seogwipo_combined = pd.DataFrame({
    'address_map': ['제주특별자치도 서귀포시'],
    'restaurant_name_2': [', '.join(seogwipo_rows['restaurant_name_2'])],
    'restaurant_count': [seogwipo_rows['restaurant_name_2'].str.split(', ').apply(len).sum()]  # 식당 개수 계산
})

# "제주특별자치도 제주시"로 시작하는 row 묶기
jeju_rows = df_cleaned[df_cleaned['address_map'].str.startswith("제주특별자치도 제주시")]
jeju_combined = pd.DataFrame({
    'address_map': ['제주특별자치도 제주시'],
    'restaurant_name_2': [', '.join(jeju_rows['restaurant_name_2'])],
    'restaurant_count': [jeju_rows['restaurant_name_2'].str.split(', ').apply(len).sum()]  # 식당 개수 계산
})

# exclude_list에 있는 읍면 데이터 유지 및 식당 개수 추가 (loc 사용)
exclude_rows = df_cleaned[df_cleaned['address_map'].isin(exclude_list)].copy()
exclude_rows.loc[:, 'restaurant_count'] = exclude_rows['restaurant_name_2'].str.split(', ').apply(len)

# 최종 결과 병합: exclude_list 데이터 + 묶인 서귀포시 + 묶인 제주시
result_df = pd.concat([exclude_rows, seogwipo_combined, jeju_combined])

# "제주특별자치도 제주시 추자면" row 삭제
result_df = result_df[result_df['address_map'] != "제주특별자치도 제주시 추자면"]

# 결과 저장
result_df.to_csv('new_address_map_restaurant_names_with_count.csv', index=False)

# 각 address_map 별 식당 개수 출력
for index, row in result_df.iterrows():
    print(f"Address: {row['address_map']}, Number of Restaurants: {row['restaurant_count']}")

print("완료되었습니다. 결과는 'new_address_map_restaurant_names_with_count.csv' 파일에 저장되었습니다.")

# 주소에서 "제주특별자치도"를 제거할 읍면 리스트
address_list = [
    "서귀포시 남원읍", "서귀포시 대정읍", "서귀포시 성산읍", "서귀포시 안덕면", "서귀포시 표선면",
    "제주시 구좌읍", "제주시 애월읍", "제주시 우도면", "제주시 조천읍", "제주시 한경면", "제주시 한림읍"
]

# "제주특별자치도"를 제거한 주소 변경
df = pd.read_csv('new_address_map_restaurant_names_with_count.csv')
df['address_map'] = df['address_map'].str.replace("제주특별자치도 ", "")

# "서귀포시 (제주특별자치도 남부)" 및 "제주시 (제주특별자치도 북부)"로 수정
df['address_map'] = df['address_map'].replace("서귀포시", "서귀포시 (제주특별자치도 남부)")
df['address_map'] = df['address_map'].replace("제주시", "제주시 (제주특별자치도 북부)")

# 변경된 데이터 저장
df.to_csv('modified_new_address_map_restaurant_names.csv', index=False)

print("주소 수정이 완료되었습니다. 파일은 'modified_new_address_map_restaurant_names.csv'로 저장되었습니다.")

# 두 개의 CSV 파일 읽기
modified_df = pd.read_csv('modified_new_address_map_restaurant_names.csv')
full_combined_df = pd.read_csv('full_combined_with_address_map.csv')

# 업데이트 성공 및 실패를 기록할 리스트
update_log = []

# full_combined_df에서 각 row의 restaurant_name_2 리스트를 순회하면서 modified_df의 address_map을 찾아서 업데이트
for i, full_row in full_combined_df.iterrows():
    # full_combined_df의 restaurant_name_2 값이 NaN이 아닌지 확인하고 문자열로 변환
    if pd.notna(full_row['restaurant_name_2']):
        full_restaurant_name = str(full_row['restaurant_name_2']).strip()
    
        # modified_df에서 일치하는 restaurant_name_2가 있는 row 찾기
        modified_match_found = False
        for j, modified_row in modified_df.iterrows():
            # modified_df에서 해당 row의 restaurant_name_2 리스트를 쉼표로 구분하여 변환
            modified_restaurant_list = modified_row['restaurant_name_2'].replace('"', '').split(', ')
            
            # 각 식당 이름과 비교하여 일치하는 식당을 찾기
            if full_restaurant_name in map(str.strip, modified_restaurant_list):
                # address_map을 modified_df의 address_map으로 업데이트
                full_combined_df.loc[i, 'address_map'] = modified_row['address_map']
                update_log.append(f"'{full_restaurant_name}'의 address_map이 '{modified_row['address_map']}'로 업데이트되었습니다.")
                modified_match_found = True
                break

        # 일치하는 식당을 찾지 못한 경우 로그에 기록
        if not modified_match_found:
            update_log.append(f"'{full_restaurant_name}'에 대한 address_map을 modified_new_address_map.csv에서 찾지 못했습니다.")
    else:
        update_log.append(f"'{full_row['restaurant_name_2']}'에 대한 값이 존재하지 않습니다.")

# 결과를 새로운 CSV 파일로 저장
full_combined_df.to_csv('updated_full_combined_with_address_map.csv', index=False)

# 업데이트 로그 출력
print("\n업데이트 로그:")
for log_entry in update_log:
    print(log_entry)

print("\n식당의 address_map이 업데이트된 파일은 'updated_full_combined_with_address_map.csv'로 저장되었습니다.")
