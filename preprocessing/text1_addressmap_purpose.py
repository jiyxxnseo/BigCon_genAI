# 신한카드 데이터에서 스트림릿 기준으로 "address_map" 칼럼 생성 코드
import pandas as pd
import numpy as np

df= pd.read_csv('/root/BigCon_genAI/data/shinhancard_data_with_text.csv')


dining_types = [
    '가정식', '단품요리 전문', '일식', '치킨', '중식', '분식', '햄버거', '양식', '맥주/요리주점', '피자', 
    '샌드위치/토스트', '꼬치구이', '기타세계요리', '구내식당/푸드코트', '도시락', '동남아/인도음식', 
    '패밀리 레스토랑', '기사식당', '야식', '스테이크', '포장마차', '부페', '민속주점'
]
cafe_types = [
    '커피', '베이커리', '아이스크림/빙수', '차', '떡/한과', '도너츠', '주스', '샌드위치/토스트'
]

# Create the 목적 column based on conditions
df['목적'] = df['판매음식종류'].apply(lambda x: '식사' if x in dining_types else ('카페/디저트' if x in cafe_types else '기타'))


# 'address_2'에서 첫 세 단어를 추출하는 함수 정의
def extract_address_map(address):
    if isinstance(address, str):  # 값이 문자열인지 확인
        return ' '.join(address.split()[:3])
    else:
        return None  # 문자열이 아닌 값에 대해 None 반환
    
df['address_map'] = df['지역'].apply(extract_address_map)


address_list = [
    "서귀포시 남원읍", "서귀포시 대정읍", "서귀포시 성산읍", "서귀포시 안덕면", "서귀포시 표선면",
    "제주시 구좌읍", "제주시 애월읍", "제주시 우도면", "제주시 조천읍", "제주시 한경면", "제주시 한림읍", "제주시 추자면"
]

def categorize_address(address):
    if address in address_list:
        return address
    elif address.startswith('제주시'):
        return '제주시 (제주특별자치도 북부)'
    elif address.startswith('서귀포시'):
        return '서귀포시 (제주특별자치도 남부)'
    else:
        return 'NA'
    

df['address_map'] = df['address_map'].apply(categorize_address)