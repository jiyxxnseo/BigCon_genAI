import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import requests

# 세션 상태에서 페이지 상태를 관리
if 'page' not in st.session_state:
    st.session_state.page = 'main'
    
# 챗봇 대화 기록 상태 관리
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 페이지 이동 함수
def go_to_next_page():
    st.session_state.page = 'next_page'

# 메인 페이지
if st.session_state.page == 'main':
    
    # CSS for changing the entire background color and styling the page
    st.markdown(
        """
        <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

        /* 기본 마진과 패딩 제거 */
        body {
            margin: 0;
            padding: 0;
        }
        
        /* Streamlit 전체 페이지의 배경을 변경하기 위한 설정 */
        .stApp {
            background-color: #ffefcc;
            font-family: 'Pretendard', sans-serif; /* 폰트 적용 */
            color: black; /* 기본 텍스트 색상 */
            padding: 0; /* 추가적인 패딩 제거 */
        }
        
        /* 상단 여백 제거 */
        .block-container {
            padding-top: 0;
            padding-bottom: 0;
            padding-right: 0;
        }
        
        /* 상단 여백 제거를 위한 추가 설정 */
        .css-18e3th9 {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            padding-right: 0 !important;
        }
        
        iframe {
            width: 100% !important;
            height: 100% !important;
            min-height: 400px;
            border: none; /* 검은 테두리 없애기 */
        }

        .full-width-banner {
            position: relative;
            background-image: url('https://github.com/gina261/bigcontest_genAI/blob/main/images/banner.png?raw=true');
            background-size: cover; /* 이미지 크기를 전체 영역에 맞춤 */
            background-position: center;
            height: 470px; /* 배너의 높이 설정 */
            width: 100vw; /* 페이지의 전체 너비를 사용 */
            margin-left: calc(-50vw + 50%); /* 페이지 중앙 정렬 후 왼쪽으로 이동 */
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            z-index: 1;
            flex-direction: column; /* 세로 방향 정렬을 위한 추가 */
        }

        /* 배너 텍스트 스타일 */
        .full-width-banner h1 {
            font-size: 3em;
            margin: 0;
            color: white;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5); /* 텍스트에 그림자 추가 */
        }

        /* 배경 큰 글씨 */
        .centered-text {
            font-size: 1.2em;
            font-weight: 650;
            margin: 0px 0 40px 0; /* 위쪽에 0px, 아래쪽에 20px 마진 추가 */
            text-align: center; /* 텍스트 중앙 정렬 */
            color: black;
        }

        /* 배경 중간 글씨 */
        .centered-subtext {
            font-size: 1.0em;
            margin: 20px 0 20px 0; /* 위쪽과 아래쪽에 20px 마진 추가 */
            text-align: center; /* 텍스트 중앙 정렬 */
            color: black;
        }

        .centered-subtext.last {
            margin-top: -10px;
            margin-bottom: -20px; /* 마지막 텍스트와 박스 사이의 간격을 추가 */
        }
        
        .centered-subtext.first {
            margin-top: -5px;
            margin-bottom: 10px;
        }

        /* 박스 스타일 */
        .box {
            background-image: url('https://github.com/gina261/bigcontest_genAI/blob/main/images/box1.png?raw=true');
            background-size: 500px;
            background-position: center; /* 이미지 중앙 정렬 */
            background-repeat: no-repeat; /* 이미지 반복 방지 */
            padding: 50px 0 20px 0; /* 상단 50px 여백, 하단 20px */
            border-radius: 0px;
            margin: 50px 0 20px 0; /* 상단 50px 하단 20px 마진 추가 */
            color: white;
            display: flex;
            justify-content: center;
            align-items: flex-start; /* 텍스트를 박스 상단에서부터 정렬 */
            height: 250px; /* 박스 높이 설정 */
        }
        
        .box h3 {
            font-size: 1.2em;
            font-weight: 550;
            margin: 0;
            text-align: center;
            color: white;
            width: 100%;
            padding-top: 133px; /* 텍스트와 상단 간격 설정 */
            padding-left: 30px;
        }

        /* 새 박스 스타일 */
        .box-2 {
            background-image: url('https://github.com/gina261/bigcontest_genAI/blob/main/images/box2.png?raw=true');
            background-size: 500px;
            background-position: center;
            background-repeat: no-repeat;
            padding: 20px;
            border-radius: 0px;
            margin: 100px 0 20px 0; /* 상단에 80px, 하단에 20px 마진 추가 */
            color: white;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            height: 100px;
            text-align: center;
        }
        
        .box-2 h3 {
            font-size: 1.2em;
            font-weight: 550;
            margin: 0;
            text-align: center;
            color: white;
            width: 100%;
            padding-top: 17px;
            padding-left: 40px
        }
        
        .box-2 h4 {
            font-size: 1.2em;
            font-weight: 550;
            margin: 0;
            text-align: center;
            color: white;
            width: 100%;
            padding-top: 17px;
            padding-left: 30px
        }

        /* 레이블 스타일 */
        .custom-label {
            color: black;
            font-family: 'Pretendard', sans-serif;
            font-weight: 400;
            font-size: 1em;
            margin-bottom: -25px;
        }
        
        /* Selectbox 내부 옵션의 스타일 변경 */
        div[data-baseweb="select"] > div {
            background-color: white !important;
            color: black !important;
            border: white !important;
            border-radius: 25px;
            height: 50px;
            display: flex;
            align-items: center; /* 텍스트를 수직 중앙 정렬 */
            padding-left: 10px; /* 텍스트 왼쪽 패딩 추가 */
        }

        /* Selectbox 크기 조정 */
        .stSelectbox div[data-baseweb="select"] {
            max-width: 250px;  /* selectbox의 최대 너비 설정 */
            margin-bottom: 20px;  /* selectbox와 아래 내용 간의 간격 설정 */
        }
        
        /* 날짜 선택 박스의 외부 회색 컨테이너 제거 */
        .stDateInput div {
            background-color: transparent !important; /* 배경색 투명하게 */
            box-shadow: none !important; /* 그림자 제거 */
            border: transparent !important;
        }
        
        /* 날짜 선택 박스 내부 스타일 */
        input[type='text'] {
            background-color: white !important; /* 내부 배경을 흰색으로 설정 */
            color: black !important;
            border: white !important;
            border-radius: 25px;
            height: 50px !important; /* 높이를 50px로 설정 */
            display: flex;
            align-items: center;
            padding-left: 20px !important;
        }
        
        .box_whatIsSelected {
            background-color: white;
            border-radius: 25px;
            height: 50px;
            width: 400px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0 auto;
            overflow-x: auto;
            white-space: nowrap;
        }
        
        /* 채팅 첫 입력 박스 */
        input.first {
            background-color: #ffffff;
            border: 2px solid #ffffff;
            border-radius: 15px;
            padding: 10px;
            width: 400px;
            height: 60px;
            font-size: 1em;
            color: #000;
            display: block;
            margin: 20px auto;
        }
        input.custom-input::placeholder {
            color: #888;
        }
        
        .region-label {
            font-weight: 200;
        }
        .region-names {
            font-weight: 400;
        }
        .text-bold {
            font-weight: 650;
        }
        .spacing-100px {
            margin-bottom: 100px;
        }
        
        
        </style>
        """,
        unsafe_allow_html=True
    )

    # HTML for the full-width banner and the centered texts below it
    st.markdown(
        """
        <div class="full-width-banner">
            <h1></h1>
        </div>
        <div class="centered-text">
            반갑습니다. 오늘 어떤 하루를 보내고 계신가요?
        </div>
        <div class="centered-subtext">
            당신의 기분에 맞는 제주 맛집을 추천해드리겠습니다.
        </div>
        <div class="centered-subtext last">
            추천을 위해 몇 가지 질문에 답해주세요.
        </div>
        """,
        unsafe_allow_html=True
    )

    # 날짜, 시간대, 인원수 선택 위젯을 한 행에 배치
    st.markdown(
        """
        <div class="box">
            <h3>1. 언제, 누구와 방문할 예정이신가요?</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 3개의 열을 생성하여 위젯을 한 행에 배치
    col1, col2, col3 = st.columns(3)

    # '선택 안함' 옵션을 추가한 selectbox를 사용하여 날짜 선택 유무 결정
    with col1:
        st.markdown("<div class='custom-label'>날짜를 선택해주세요.</div>", unsafe_allow_html=True)
        date_option = st.selectbox("", ["선택 안함", "날짜 선택"])

        # 선택한 옵션에 따라 date_input 표시
        if date_option == "날짜 선택":
            selected_date = st.date_input("")
        else:
            selected_date = None

        
    with col2:
        st.markdown("<div class='custom-label'>시간대를 선택해주세요.</div>", unsafe_allow_html=True)
        time_slot = st.selectbox(
            "", 
            ("선택 안함", "아침", "점심", "오후", "저녁", "밤")
        )

    with col3:
        st.markdown("<div class='custom-label'>인원수를 선택해주세요.</div>", unsafe_allow_html=True)
        members_num = st.selectbox(
            "", 
            ("선택 안함", "혼자", "2명", "3명", "4명 이상")
        )


    # 새 박스를 추가
    st.markdown(
        """
        <div class="box-2">
            <h3>2. 방문 목적이 무엇인가요?</h3>
        </div>
        """,
        unsafe_allow_html=True
    )


    # 중앙에 selectbox를 배치
    col_center = st.columns([1, 1, 1])
    with col_center[1]:
        visit_purpose = st.selectbox(
            "",
            ("선택 안함", "식사", "카페/디저트")
        )
        

    st.markdown(
        """
        <div class="box-2">
            <h4>3. 어디로 가시나요?</h4>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="centered-subtext first">
            두 개 이상의 지역을 선택하실 경우, 차례대로 클릭해주세요.
        </div>
        """,
        unsafe_allow_html=True
    )

    ####### 지도 구현 #######

    # 선택된 지역을 저장할 리스트 생성 (세션 상태에서 관리)
    if 'selected_regions' not in st.session_state:
        st.session_state.selected_regions = []

    # 선택 초기화 버튼 클릭 시 선택된 지역 초기화
    if st.button("선택 초기화"):
        st.session_state.selected_regions = []
        
    # 선택된 지역 텍스트를 위한 placeholder 생성
    selected_region_text = st.empty()

    # 제주도 중심 좌표
    jeju_center = [33.38, 126.6] # 기존 33.4996, 126.5312

    mapbox_token = st.secrets["MAPBOX_API_KEY"]

    # 커스텀 Mapbox 스타일 URL 적용
    mapbox_style = 'mapbox://styles/gina261/cm2f34dvz000g01pygoj0g41c'
    custom_style_url = f'https://api.mapbox.com/styles/v1/gina261/cm2f34dvz000g01pygoj0g41c/tiles/{{z}}/{{x}}/{{y}}?access_token={mapbox_token}'

    # Folium 지도 객체 생성
    jeju_map = folium.Map(
        location=jeju_center, 
        zoom_start=9.8,
        tiles=custom_style_url,
        attr='Mapbox',
        name='Mapbox Custom Style',
        dragging=False,
        zoom_control=False,
        scrollWheelZoom=False,
        doubleClickZoom=False
    )

    # Load GeoJSON data from GitHub link
    geojson_url = 'https://raw.githubusercontent.com/gina261/bigcontest_genAI/main/geojson/jeju_edited.geojson'
    geojson_data = requests.get(geojson_url).json()

    # Add GeoJSON data to the map with interactive features
    def on_click(feature):
        return {
            'fillColor': '#ff8015',
            'color': 'black',
            'weight': 2,
            'fillOpacity': 0.6,
            'highlight': True
        }

    geo_json = folium.GeoJson(
        geojson_data,
        name='jeju_districts',
        style_function=lambda feature: {
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0,
        },
        highlight_function=on_click,
        tooltip=folium.GeoJsonTooltip(
            fields=['adm_nm'],  # Ensure that 'adm_nm' is the field name for the region name
            aliases=['Region'],
            localize=True
        )
    ).add_to(jeju_map)

    # Streamlit에서 지도 표시
    st_data = st_folium(jeju_map, width=800, height=400)

    # 선택한 지역을 가져오기
    if st_data and st_data.get('last_active_drawing'):
        selected_region = st_data['last_active_drawing']['properties']['adm_nm']

        # 지역이 이미 선택된 리스트에 없으면 추가
        if selected_region not in st.session_state.selected_regions:
            st.session_state.selected_regions.append(selected_region)
            
    # 선택된 지역 이름을 처리
    def format_region_name(region):
        region_parts = region.split(' ')
        if region_parts[0] == "제주특별자치도" and len(region_parts) >= 3:
            return region_parts[2]  # 세 번째 단어만 저장
        else:
            return region_parts[0]  # 첫 단어만 저장
        
    selected_regions_display = ", ".join([format_region_name(region) for region in st.session_state.selected_regions])

    # 선택된 지역 업데이트
    if selected_regions_display:
        selected_region_text.markdown(
            f"""
            <div class="box_whatIsSelected">
                <span class="region-label">선택된 지역:&nbsp;</span> <span class="region-names">{selected_regions_display}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # 선택된 지역이 없을 때 텍스트 표시
        selected_region_text.markdown(
            """
            <div class="box_whatIsSelected">
                선택된 지역 없음
            </div>
            """,
            unsafe_allow_html=True
        )
        
    st.markdown('<div class="spacing-100px"></div>', unsafe_allow_html=True)
        
    st.markdown(
        """
        <div class="centered-subtext">
            감사합니다! 이제 오늘의 <span class="text-bold">기분</span>이나 <span class="text-bold">상황</span>을 입력해주세요. 그에 맞는 제주의 멋진 곳을 추천해드립니다.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # user_firstInput = st.text_input("", placeholder="여기에 입력하세요", key="user_input")
    
    # st.markdown(
    #     f"""
    #     <input class="custom-input" type="text" placeholder="여기에 입력하세요" value="{user_firstInput}">
    #     """,
    #     unsafe_allow_html=True
    # )
    
    if st.button("입력"):
        go_to_next_page()
        
####### 두 번째 페이지 #######
elif st.session_state.page == 'next_page':
    
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    
    def chatbot_response(user_input):
        # 챗봇 로직 구현
        if user_input:
            return f"챗봇: {user_input[::-1]}"
        return ""
    
    # 기본 설정
    st.markdown(
        """
        <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        
        /* Streamlit 전체 페이지의 배경을 변경하기 위한 설정 */
        .stApp {
            background-color: #ffefcc;
            font-family: 'Pretendard', sans-serif;
            color: black; /* 기본 텍스트 색상 */
            padding: 0;
        }
        
        /* 채팅 컨테이너 스타일 */
        .chat-container {
            height: calc(100vh - 150px); /* 상단과 입력창을 제외한 영역 */
            overflow-y: auto;
            display: flex;
            flex-direction: column-reverse; /* 대화가 아래에서 위로 쌓이도록 */
            padding: 20px;
            margin-bottom: 60px; /* 입력창 영역을 위해 여백 추가 */
        }
        
        /* 채팅 박스 스타일 */
        .chat-box {
            background-color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            font-family: 'Pretendard', sans-serif;
            max-width: 70%;
            word-wrap: break-word;
        }
        .user-msg {
            color: black;
            align-self: flex-start;
        }
        .bot-msg {
            color: #FF7F50;
            align-self: flex-end;
        }
        
        /* 입력 영역 고정 */
        .input-container {
            position: fixed;
            bottom: 30px;
            left: 20%;
            width: 60%;
            min-height: 60px;
            max-height: 220px;
            background-color: #fff;
            padding: 10px 25px;
            border-radius: 30px;
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            box-sizing: border-box;
            transition: height 0.3s ease;
        }
        
        .chat-input {
            width: calc(100% - 100px);
            min-height: 50px;
            max-height: 200px;
            border: none;
            font-size: 16px;
            color: black;
            padding: 10px;
            box-sizing: border-box;
        }
        
        .send-btn {
            width: 80px;
            height: 30px;
            background-color: #ff8015;
            color: white;
            border: none;
            border-radius: 30px;
            cursor: pointer;
            margin-left: 7px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    
    ####### 챗봇 구현 #######
    
    # 사용자 입력 받기
    st.markdown(
        """
        <div class="input-container">
            <textarea class="chat-input" id="chat_input" placeholder="메시지를 입력하세요" oninput="adjustHeight(this)"></textarea>
            <button class="send-btn" onclick="sendMessage()">입력</button>
        </div>

        <script>
        function adjustHeight(input) {
            input.style.height = "auto"; // 먼저 높이를 자동으로 설정하여 기존 값을 초기화
            input.style.height = (input.scrollHeight) + "px"; // 내용을 기준으로 높이를 조정
        }

        function sendMessage() {
            var input = document.getElementById('chat_input').value;
            if (input) {
                console.log('User input:', input);
                // 여기에 추가적인 처리 로직을 작성
            }
        }
        </script>
        """,
        unsafe_allow_html=True
    )