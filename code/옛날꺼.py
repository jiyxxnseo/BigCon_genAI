import streamlit as st
import folium
from streamlit_folium import st_folium

# CSS for changing the entire background color and styling the page
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic&display=swap');

    /* Streamlit 전체 페이지의 배경을 변경하기 위한 설정 */
    .stApp {
        background-color: #020202;
        font-family: 'Nanum Gothic', sans-serif; /* Nanum Gothic 폰트 적용 */
        color: black; /* 기본 텍스트 색상 */
    }

    .full-width-banner {
        position: relative;
        background-image: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url('https://ifh.cc/g/tyYadc.jpg'); /* 반투명 검정색 오버레이와 이미지 */
        background-size: cover; /* 이미지 크기를 전체 영역에 맞춤 */
        background-position: center; /* 이미지 중앙 정렬 */
        height: 500px; /* 배너의 높이 설정 */
        width: 100vw; /* 페이지의 전체 너비를 사용 */
        margin-left: calc(-50vw + 50%); /* 페이지 중앙 정렬 후 왼쪽으로 이동 */
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        z-index: 1;
        flex-direction: column; /* 세로 방향 정렬을 위한 추가 */
    }

    /* 텍스트 스타일 */
    .full-width-banner h1 {
        font-size: 3em;
        margin: 0;
        color: white;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5); /* 텍스트에 그림자 추가 */
    }

    .centered-text {
        font-size: 1.5em;
        margin: 40px 0 20px 0; /* 위쪽에 40px, 아래쪽에 20px 마진 추가 */
        text-align: center; /* 텍스트 중앙 정렬 */
        color: white;
    }

    .centered-subtext {
        font-size: 1.2em;
        margin: 20px 0 20px 0; /* 위쪽과 아래쪽에 20px 마진 추가 */
        text-align: center; /* 텍스트 중앙 정렬 */
        color: white;
    }

    .centered-subtext.last {
        margin-bottom: 150px; /* 마지막 텍스트와 박스 사이의 간격을 추가 */
    }

    /* 박스 스타일 */
    .box {
        background-image: url('https://ifh.cc/g/66L6Y8.png');
        background-size: cover; /* 이미지 크기를 전체 영역에 맞춤 */
        background-position: center; /* 이미지 중앙 정렬 */
        background-repeat: no-repeat; /* 이미지 반복 방지 */
        padding: 20px;
        border-radius: 0px;
        margin: 50px 0; /* 상단과 하단에 50px 마진 추가 */
        color: white;
        display: flex;
        align-items: center; /* 수직 중앙 정렬 */
        height: 100px; /* 박스 높이 설정 */
    }

    /* 새 박스 스타일 */
    .box-2 {
        background-image: url('https://ifh.cc/g/n7tgX0.png');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        padding: 20px;
        border-radius: 0px;
        margin: 100px 0 50px 0; /* 상단에 50px, 하단에 50px 마진 추가 */
        color: white;
        display: flex;
        align-items: center;
        height: 100px;
    }

    .box h3, .box-2 h3 {
        font-size: 1.2em;
        margin: 0;
        text-align: left;
        color: white;
        width: 100%;
        text-align: center; /* 텍스트 중앙 정렬 */
    }

    /* 레이블 스타일 */
    .custom-label {
        color: white;
        font-size: 1em;
        margin-bottom: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# HTML for the full-width banner and the centered texts below it
st.markdown(
    """
    <div class="full-width-banner">
        <h1>Welcome to team 예쁘DA</h1>
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
        <h3>언제, 누구와 가시나요?</h3>
    </div>
    """,
    unsafe_allow_html=True
)

# 3개의 열을 생성하여 위젯을 한 행에 배치
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<div class='custom-label'>날짜를 선택하세요 :</div>", unsafe_allow_html=True)
    selected_date = st.date_input("")
    
with col2:
    st.markdown("<div class='custom-label'>시간대를 선택하세요 :</div>", unsafe_allow_html=True)
    time_slot = st.selectbox(
        "", 
        ("아침", "점심", "저녁")
    )

with col3:
    st.markdown("<div class='custom-label'>인원수를 선택하세요 :</div>", unsafe_allow_html=True)
    members_num = st.selectbox(
        "", 
        ("혼자", "2명", "3명", "4명 이상")
    )
    
st.write(f"{selected_date} {time_slot}에 {members_num} 방문할 예정입니다.")

# 새 박스를 추가
st.markdown(
    """
    <div class="box-2">
        <h3>어디로 가시나요?</h3>
    </div>
    """,
    unsafe_allow_html=True
)

# 제주도 중심 좌표
jeju_center = [33.4996, 126.5312]

# Folium 지도 객체 생성
jeju_map = folium.Map(location=jeju_center, zoom_start=10)

# 마커 추가 예시
folium.Marker(
    location=[33.4996, 126.5312],
    popup="제주시",
    icon=folium.Icon(color="blue")
).add_to(jeju_map)

# Streamlit에서 지도 표시
st_data = st_folium(jeju_map, width=700, height=500)