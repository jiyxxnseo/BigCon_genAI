import pandas as pd

# 1. 신한카드 데이터 불러오기 및 중복 제거
original_shinhan_data = pd.read_csv('/Users/BigCon/data/신한카드데이터_컬럼변경.csv').drop(columns=['Unnamed: 0'], errors='ignore')

# 데이터를 역순으로 정렬하고 중복된 가맹점명과 주소를 제거
final_shinhan_data = original_shinhan_data.iloc[::-1].reset_index(drop=True).drop_duplicates(subset=['가맹점명', '주소'])

# 결과를 CSV 파일로 저장
final_shinhan_data.to_csv('./final_shinhan_data.csv')

# 2. 컬럼명 한글로 변경
final_shinhan_data.rename(columns={
    'YM': '기준연월', 'MCT_NM': '가맹점명', 'OP_YMD': '개설일자', 'MCT_TYPE': '판매음식종류',
    'ADDR': '지역', 'UE_CNT_GRP': '이용건수', 'UE_AMT_GRP': '이용금액',
    'UE_AMT_PER_TRSN_GRP': '건당평균이용금액구간', 'MON_UE_CNT_RAT': '월요일이용건수비중', 'TUE_UE_CNT_RAT': '화요일이용건수비중',
    'WED_UE_CNT_RAT': '수요일이용건수비중', 'THU_UE_CNT_RAT': '목요일이용건수비중', 'FRI_UE_CNT_RAT': '금요일이용건수비중',
    'SAT_UE_CNT_RAT': '토요일이용건수비중', 'SUN_UE_CNT_RAT': '일요일이용건수비중',
    'HR_5_11_UE_CNT_RAT': '5시11시이용건수비중', 'HR_12_13_UE_CNT_RAT': '12시13시이용건수비중',
    'HR_14_17_UE_CNT_RAT': '14시17시이용건수비중', 'HR_18_22_UE_CNT_RAT': '18시22시이용건수비중',
    'HR_23_4_UE_CNT_RAT': '23시4시이용건수비중', 'LOCAL_UE_CNT_RAT': '현지인이용비중',
    'RC_M12_MAL_CUS_CNT_RAT': '최근12개월남성회원수비중', 'RC_M12_FME_CUS_CNT_RAT': '최근12개월여성회원수비중',
    'RC_M12_AGE_UND_20_CUS_CNT_RAT': '20대이하고객수비중', 'RC_M12_AGE_30_CUS_CNT_RAT': '30대고객수비중',
    'RC_M12_AGE_40_CUS_CNT_RAT': '40대회원수비중', 'RC_M12_AGE_50_CUS_CNT_RAT': '50대회원수비중',
    'RC_M12_AGE_OVR_60_CUS_CNT_RAT': '60대이상회원수비중'
}, inplace=True)

# 컬럼명을 변경한 데이터를 새로운 CSV 파일로 저장
final_shinhan_data.to_csv('./final_shinhan_data_rename.csv', index=False)

# 3. 각 행에 대한 텍스트 설명 생성
final_shinhan_data['text1'] = final_shinhan_data.apply(lambda row: (
    f"{row['기준연월']} 기준 {row['가맹점명']} (개설일: {row['개설일자']})의 업종은 {row['판매음식종류']}, "
    f"위치는 {row['지역']}입니다. "
    f"이용건수는 동일 업종 내 상위 {row['이용건수']}이고, 이용금액은 {row['이용금액']}, "
    f"건당 평균 이용금액은 {row['건당평균이용금액구간']}입니다. "
    f"요일별 이용건수 비중은 월요일 {row['월요일이용건수비중']}, 화요일 {row['화요일이용건수비중']}, "
    f"수요일 {row['수요일이용건수비중']}, 목요일 {row['목요일이용건수비중']}, "
    f"금요일 {row['금요일이용건수비중']}, 토요일 {row['토요일이용건수비중']}, "
    f"일요일 {row['일요일이용건수비중']}입니다. "
    f"시간대별 이용건수 비중은 5시~11시 {row['5시11시이용건수비중']}, 12시~13시 {row['12시13시이용건수비중']}, "
    f"14시~17시 {row['14시17시이용건수비중']}, 18시~22시 {row['18시22시이용건수비중']}, "
    f"23시~4시 {row['23시4시이용건수비중']}입니다. "
    f"현지인 이용 비중은 {row['현지인이용비중']}이며, 최근 12개월 동안 남성 회원 비중은 {row['최근12개월남성회원수비중']}, "
    f"여성 회원 비중은 {row['최근12개월여성회원수비중']}입니다. "
    f"연령대별 고객 비중은 20대 이하 {row['20대이하고객수비중']}, 30대 {row['30대고객수비중']}, "
    f"40대 {row['40대회원수비중']}, 50대 {row['50대회원수비중']}, 60대 이상 {row['60대이상회원수비중']}입니다."
), axis=1)

# 텍스트 설명이 포함된 데이터를 저장
final_shinhan_data.to_csv('./final_shinhan_data_with_text.csv', index=False)

# 결과 확인
print(final_shinhan_data[['가맹점명', 'text1']].head())