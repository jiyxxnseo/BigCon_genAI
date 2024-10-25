import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# CSV 파일에서 데이터 로드
df_restaurants = pd.read_csv('/JEJU_MCT_DATA_v2_unique.csv', encoding='cp949')

# MCT_NM 열에서 식당 이름을 리스트로 추출 (1~2313개의 식당)
restaurant_list = df_restaurants['MCT_NM'].tolist()

# 수집된 데이터 저장할 리스트
data = []

# 웹 드라이버 옵션 설정
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")

# 웹 드라이버 초기화 (chromedriver 경로를 명시해 주세요)
driver = webdriver.Chrome(options=options)

# 카카오 맵으로 이동
source_url = "https://map.kakao.com/"
driver.get(source_url)

# 검색 및 상세보기 링크 수집 함수 (BeautifulSoup 사용)
def search_and_collect_detail_links(restaurant_name):
    try:
        # '제주'를 붙여서 검색어 구성
        search_query = f"제주 {restaurant_name}"
        
        # 검색창에 식당 이름 입력
        searchbox = driver.find_element(By.ID, 'search.keyword.query')
        searchbox.clear()
        searchbox.send_keys(search_query)  # '제주 식당이름' 입력

        # 검색 버튼 클릭
        searchbutton = driver.find_element(By.ID, 'search.keyword.submit')
        driver.execute_script("arguments[0].click();", searchbutton)  # 검색 버튼 클릭

        # 검색 결과 로드 대기
        time.sleep(2)

        # 첫 번째 결과 클릭
        first_result = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.link_name"))
        )
        driver.execute_script("arguments[0].click();", first_result)

        # 페이지 소스를 가져와 BeautifulSoup으로 파싱
        time.sleep(2)  # 페이지 로드 대기
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # 첫 번째 상세보기 링크만 찾기
        moreview = soup.find("a", attrs={"class": "moreview"})
        if moreview:
            page_url = moreview.get("href")  # 첫 번째 상세보기 링크의 href 속성 추출
            data.append([restaurant_name, page_url])  # 식당 이름과 링크 저장
            print(f"{restaurant_name}의 첫 번째 상세보기 링크: {page_url}")
        else:
            data.append([restaurant_name, "없음"])  # 링크가 없으면 '없음'으로 표시
            print(f"{restaurant_name}의 상세보기 링크가 없습니다.")
            
    except Exception as e:
        print(f'{restaurant_name}에서 상세보기 링크를 확인하는 중 오류 발생: {e}')
        data.append([restaurant_name, "없음"])  # 오류 발생 시도 '없음'으로 처리

# 리스트에 있는 식당을 순회하면서 상세보기 링크 수집
for restaurant in restaurant_list:
    search_and_collect_detail_links(restaurant)
    time.sleep(3)  # 각 검색 사이에 대기 시간 추가

# 크롤링 후 드라이버 종료
driver.quit()

# 데이터프레임 생성
df = pd.DataFrame(data, columns=["restaurant_name", "detail_link"])

# 데이터프레임을 CSV 파일로 저장
df.to_csv("restaurant_detail_links.csv", index=False)

# 데이터프레임 출력 확인
print(df.head())
