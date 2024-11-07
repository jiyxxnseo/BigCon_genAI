import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from bs4 import BeautifulSoup
from datetime import datetime

# CSV 파일로부터 상세보기 링크 로드
csv_file_path = '/Users/macbook/Documents/2024_빅콘테스트/신한카드데이터_분석/Week 3 - Finalizing_crawling_code/restaurant_detail_links.csv'  # 업로드한 파일 경로에 맞게 수정
df_restaurants = pd.read_csv(csv_file_path)

# 기존 크롤링 데이터를 로드
output_file_path = 'restaurant_info_data_final_194.csv'
try:
    df = pd.read_csv(output_file_path)  # 기존 데이터를 불러옴
    print(f"기존 데이터 로드 완료: {len(df)}개의 레코드")
except FileNotFoundError:
    df = pd.DataFrame(columns=[
        "restaurant_name", "category", "business_hours", "tags", 
        "restaurant_info", "restaurant_facility", "restaurant_introduction", 
        "total_reviews", "overall_rating", "menu_info", "all_reviews", "review_match"
    ])
    print("새로운 파일로 데이터 저장을 시작합니다.")

# 웹 드라이버 옵션 설정
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")

# 웹 드라이버 초기화
driver = webdriver.Chrome(options=options)

# 상세보기 페이지에서 정보와 리뷰 데이터 수집
def get_restaurant_data(page_url, restaurant_name):
    driver.get(page_url)
    time.sleep(2)  # 페이지 로드 대기

    # 페이지 소스를 BeautifulSoup으로 파싱
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:
        # 카테고리, 전체 리뷰, 별점 등 정보 수집
        category_element = soup.select_one("#mArticle > div.cont_essential > div:nth-child(1) > div.place_details > div > div.location_evaluation > span.txt_location")
        category_text = category_element.get_text(strip=True).replace("분류:", "").strip() if category_element else "정보 없음"

        # 전체 리뷰 갯수 추출(숫자만)
        total_reviews_element = soup.select_one("#mArticle > div.cont_evaluation > strong.total_evaluation > span.color_b")
        total_reviews = int(total_reviews_element.text.strip().replace(",", "")) if total_reviews_element else 0

        # 식당 전체 별점 수집
        overall_rating_element = soup.select_one("div.ahead_info > div.grade_star > em.num_rate")
        overall_rating = overall_rating_element.text.strip() if overall_rating_element else "정보 없음"

        # 영업시간 정보 추출 (새로운 selector 적용)
        business_hours_section = soup.select_one("#mArticle > div.cont_essential > div.details_placeinfo > div:nth-child(3) > div > div.location_present > div > ul")
        business_hours = "정보 없음"
        if business_hours_section:
            # 모든 텍스트를 가져와서 공백 제거 후 결합
            business_hours = " | ".join([line.get_text(strip=True).replace("더보기", "").strip() for line in business_hours_section.find_all("li")])
       
        # 모든 h4 태그를 찾음 (추후 태그, 레스토랑 정보, 시설정보 수집 위함)
        h4_tags = soup.select("#mArticle > div.cont_essential > div.details_placeinfo > div > h4")
        
        # 태그 추출
        tags = "정보 없음"
        h4_tags = soup.select("#mArticle > div.cont_essential > div.details_placeinfo > div > h4")
    
        for h4_tag in h4_tags:
            span_tag = h4_tag.select_one("span.ico_comm.ico_tag")
            if span_tag:
                next_div = h4_tag.find_next_sibling("div")
                if next_div:
                    tags = ", ".join([tag.get_text(strip=True) for tag in next_div.find_all("a")])
                    break

        # 레스토랑 정보 수집
        restaurant_info = "정보 없음"
        
        for h4_tag in h4_tags:
            # h4 태그 안에 span이 있고, 그 클래스가 'ico_comm ico_delivery'인 경우
            span_tag = h4_tag.select_one("span.ico_comm.ico_delivery")
            if span_tag:
                # h4 다음 형제인 div 태그에서 레스토랑 정보를 추출
                next_div = h4_tag.find_next_sibling("div")
                if next_div:
                    restaurant_info = next_div.get_text(strip=True)
                    break  # 조건을 만족하는 첫 번째 정보를 찾으면 종료
        
        # 레스토랑 시설 정보 수집
        facility_elements = soup.select("#mArticle > div.cont_essential > div.details_placeinfo > div.placeinfo_default.placeinfo_facility > ul li")
        restaurant_facility = ", ".join([facility.find("span", class_="color_g").text.strip() for facility in facility_elements]) if facility_elements else "정보 없음"

        restaurant_introduction_element = soup.select_one("#mArticle > div.cont_essential > div.details_placeinfo > div.placeinfo_default.open_on > div > p")
        restaurant_introduction = restaurant_introduction_element.text.strip() if restaurant_introduction_element else "정보 없음"

        
        # 메뉴 정보 추출
        menu_section = soup.select_one("#mArticle > div.cont_menu > ul")
        menu_info = "정보 없음"
        if menu_section:
            # 메뉴 정보에서 이름과 가격을 구분하여 "명: , 가격: " 형식으로 저장
            menu_info_list = []
            for li in menu_section.find_all("li"):
                menu_text = li.get_text(strip=True)
                
                # "가격" 앞의 내용을 '명:', 가격 뒤에는 '가격:'으로 분리
                if "가격" in menu_text:
                    parts = menu_text.split("가격")
                    menu_name = parts[0].strip()
                    menu_price = parts[1].strip().lstrip(":").strip()  # 앞쪽에 있는 ":"를 제거
                    
                    # '명:'이나 '가격:'이 중복되지 않도록 처리
                    if not menu_name.startswith("명:"):
                        menu_name = f"명: {menu_name}"
                    if not menu_price.startswith("가격:"):
                        menu_price = f"가격: {menu_price}"
                    
                    formatted_menu = f"{menu_name}, {menu_price}"
                else:
                    # 가격 정보가 없는 경우 처리
                    formatted_menu = f"명: {menu_text}, 가격: 정보 없음"
                
                menu_info_list.append(formatted_menu)
            
            menu_info = " | ".join(menu_info_list)

    
        # 리뷰 데이터 수집
        reviews_collected = 0
        review_data = []  # 중복된 리뷰를 피하기 위해 리스트 사용

        # 최대 100개의 리뷰만 수집
        max_reviews = 100

        while reviews_collected < total_reviews and reviews_collected < max_reviews:
            # 현재 페이지의 리뷰와 날짜 추출
            contents_div = soup.select_one("#mArticle > div.cont_evaluation > div.evaluation_review")
            if contents_div:
                review_dates = contents_div.select("ul > li > div.unit_info > span.time_write")
                reviews = contents_div.select("ul > li > div.comment_info > p.txt_comment")

                for review_date, review in zip(review_dates, reviews):
                    review_text = review.find("span").text.strip()
                    review_tuple = (review_date.text.strip(), review_text)
                    
                    # 중복된 리뷰인지 확인하고 새로운 리뷰만 추가
                    if review_tuple not in review_data and reviews_collected < max_reviews:
                        review_data.append(review_tuple)
                        reviews_collected += 1

                # 더 많은 리뷰가 필요하면 '후기 더보기' 버튼 클릭
                if reviews_collected < max_reviews:
                    try:
                        more_review_button = driver.find_element(By.CSS_SELECTOR, '#mArticle > div.cont_evaluation > div.evaluation_review > a.link_more')
                        more_review_button.click()
                        time.sleep(2)
                        soup = BeautifulSoup(driver.page_source, 'html.parser')
                    except NoSuchElementException:
                        print("더 이상 후기 더보기 버튼이 없습니다.")
                        break
                    except ElementClickInterceptedException:
                        # 버튼이 가려져서 클릭이 방해받는 경우 스크롤 시도
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(1)
                        reviews_collected += 1
                else:
                    break

        # 리뷰가 없는 경우 기본 정보만 저장
        review_match = "일치" if len(review_data) == total_reviews else "불일치"

        if not review_data:
            df.loc[len(df)] = [restaurant_name, category_text, business_hours, tags, restaurant_info, restaurant_facility, restaurant_introduction, total_reviews, overall_rating, menu_info, "정보 없음", review_match]
        else:
            # 리뷰 데이터를 review_date 기준으로 최신순 정렬 후 2020년도 이전 리뷰 제외
            review_data_sorted = sorted(review_data, key=lambda x: x[0], reverse=True)
            valid_reviews = []
            for review_date, review_text in review_data_sorted[:max_reviews]:
                review_year = int(review_date[:4])
                if review_year >= 2020:
                    valid_reviews.append(f"{review_date}: {review_text}")

            # 리뷰들을 하나의 문자열로 결합
            all_reviews = " | ".join(valid_reviews)
            df.loc[len(df)] = [restaurant_name, category_text, business_hours, tags, restaurant_info, restaurant_facility, restaurant_introduction, total_reviews, overall_rating, menu_info, all_reviews, review_match]

        # 크롤링한 리뷰 데이터 개수와 total_reviews 비교 후 데이터프레임에 추가
        if len(review_data) != total_reviews:
            print(f"Warning: {restaurant_name} - 수집한 리뷰 개수({len(review_data)})와 total_reviews({total_reviews})가 일치하지 않습니다.")
        else:
            print(f"{restaurant_name} - 리뷰 개수 일치: {len(review_data)}")

    except Exception as e:
        print(f"{page_url}에서 데이터를 수집하는 중 오류 발생: {e}")


# 시작 trial 설정
trial = 100  # 새로 크롤링을 시작할 trial 번호
num = 10
total_entries = len(df_restaurants)

while trial <= (total_entries // num) + 1:
    print(f'{trial}번째 시도 : 인덱스 {(trial-1)*num}~{trial*num}')
    df_new = pd.DataFrame(columns=[
        "restaurant_name", "category", "business_hours", "tags", 
        "restaurant_info", "restaurant_facility", "restaurant_introduction", 
        "total_reviews", "overall_rating", "menu_info", "all_reviews", "review_match"
    ])
    
    for index, row in df_restaurants[(trial-1)*num:trial*num].iterrows():
        restaurant_name = row['restaurant_name']
        detail_link = row['detail_link']
        if detail_link != "없음":
            get_restaurant_data(detail_link, restaurant_name)
        else:
            print(f"{restaurant_name}의 상세보기 링크가 없습니다.")

    df = pd.concat([df, df_new], ignore_index=True)

    df.to_csv(f"restaurant_info_data_final_{trial}.csv", index=False)
    print(f'{trial}번째 시도 완료: 현재 데이터프레임 길이: {len(df)}')
    print('------------------------------------------')

    trial += 1

driver.quit()
