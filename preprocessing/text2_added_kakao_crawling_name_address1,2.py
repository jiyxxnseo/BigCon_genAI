import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from bs4 import BeautifulSoup

# CSV 파일로부터 상세보기 링크 로드
csv_file_path = '1_2000_restaurant_detail_links.csv'  
df_restaurants = pd.read_csv(csv_file_path)

# 새 파일로 데이터 저장 시작
output_file_path = '1_2000_restaurant_name_address.csv'
df = pd.DataFrame(columns=["restaurant_name_2", "address_1", "address_2"])

# 웹 드라이버 옵션 설정
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")

# 웹 드라이버 초기화
driver = webdriver.Chrome(options=options)

def get_restaurant_data(page_url, restaurant_name):
    driver.get(page_url)
    time.sleep(2)  # 페이지 로드 대기

    # BeautifulSoup으로 페이지 파싱
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:
        # restaurant_name_2 크롤링
        restaurant_name_2 = soup.select_one('#mArticle > div.cont_essential > div:nth-child(1) > div.place_details > div > h2').get_text(strip=True)

        # address_1 크롤링
        address_1 = soup.select_one('#mArticle > div.cont_essential > div.details_placeinfo > div:nth-child(2) > div > span.txt_address').get_text(strip=True)

        # address_2 크롤링 (address_2의 HTML 구조에 맞게 수정)
        address_2_raw = soup.select_one('#mArticle > div.cont_essential > div.details_placeinfo > div:nth-child(2) > div > span.txt_addrnum').get_text(strip=True)
        address_2 = address_2_raw.split('번지')[0].split('지번')[-1].strip()  # '지번' 이후의 주소만 추출

        # 최종 address_2 조합
        region_name = " ".join(address_1.split()[:2])  # address_1에서 "제주특별자치도 서귀포시" 추출
        address_2 = f"{region_name} {address_2}번지"  # address_2 조합

        return {
            "restaurant_name_2": restaurant_name_2,
            "address_1": address_1,
            "address_2": address_2
        }

    except NoSuchElementException:
        print(f"데이터를 찾을 수 없음: {restaurant_name}")
        return None

# 크롤링 실행
for index, row in df_restaurants.iterrows():
    if index < len(df):  # 이미 처리한 레코드 건너뛰기
        continue

    page_url = row['detail_link']
    restaurant_name = row['restaurant_name']

    # 데이터 수집
    try:
        restaurant_data = get_restaurant_data(page_url, restaurant_name)
        if restaurant_data:
            df = pd.concat([df, pd.DataFrame([restaurant_data])], ignore_index=True)

            # 수집 후 데이터 파일 저장
            df.to_csv(output_file_path, index=False)
            print(f"{restaurant_name} 정보 저장 완료.")
        
    except (NoSuchElementException, ElementClickInterceptedException) as e:
        print(f"오류 발생: {e}, {restaurant_name} 건너뜀.")
        continue

# 크롤링 완료 후 브라우저 종료
driver.quit()