import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
import requests
import numpy as np
import pandas as pd

# utils 가져오기 
from utils.config import model, df, text2_df, config, mapbox_key
from utils.sql_utils import convert_question_to_sql, execute_sql_query_on_df
from utils.faiss_utils import load_faiss_index, embed_text
from utils.user_input_detector import detect_emotion_and_context
from utils.text1_response_generator import generate_response_with_faiss, generate_gemini_response_from_results
from utils.text2_response_generator import text2faiss, recommend_restaurant_from_subset
from utils.filter_fixed_inputs import filter_fixed_address_purpose, filter_fixed_datetime_members, filter_fixed_address_purpose_text1


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
        
        /* 다크모드 */
        .st-emotion-cache-h4xjwg {
            background: #ffffff;
        }
        .st-emotion-cache-kd13nv {
            background: url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0iY3VycmVudENvbG9yIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGNvbG9yPSIjMzEzMzNGIj48ZyBjbGlwLXBhdGg9InVybCgjY2xpcDBfM18yKSI+PHBhdGggZD0iTTE0LjcwMjYgNS41MjAzN0wxMC40NjEyIDUuMTM1NDJMOC44MDQ5NSAxLjA1NjhDOC41MDcwMSAwLjMxNDQgNy40OTA0NCAwLjMxNDQgNy4xOTI1MSAxLjA1NjhMNS41MzYyNCA1LjE0NDU5TDEuMzAzNTYgNS41MjAzN0MwLjUzMjM4NyA1LjU4NDUzIDAuMjE2OTA4IDYuNTkyNzMgMC44MDQwNSA3LjEyNDMxTDQuMDIwMTggMTAuMDM4OUwzLjA1NjIyIDE0LjM2NUMyLjg4MDk1IDE1LjE1MzIgMy42OTU5NCAxNS43NzY1IDQuMzYxOTUgMTUuMzU0OUw3Ljk5ODY5IDEzLjA2MzZMMTEuNjM1NSAxNS4zNjQxQzEyLjMwMTUgMTUuNzg1NyAxMy4xMTY1IDE1LjE2MjQgMTIuOTQxMiAxNC4zNzQyTDExLjk3NzMgMTAuMDM4OUwxNS4xOTM0IDcuMTI0MzFDMTUuNzgwNSA2LjU5MjczIDE1LjQ3MzggNS41ODQ1MyAxNC43MDI2IDUuNTIwMzdaTTcuOTk4NjkgMTEuMzQ5Nkw0LjcwMzcyIDEzLjQzMDFMNS41ODAwNSA5LjUwNzMxTDIuNjcwNjMgNi44Njc2OUw2LjUwODk2IDYuNTE5NEw3Ljk5ODY5IDIuODI1NzNMOS40OTcyNiA2LjUyODU3TDEzLjMzNTYgNi44NzY4N0wxMC40MjYxIDkuNTE2NUwxMS4zMDI1IDEzLjQzOTNMNy45OTg2OSAxMS4zNDk2WiI+PC9wYXRoPjwvZz48ZGVmcz48Y2xpcFBhdGggaWQ9ImNsaXAwXzNfMiI+PHJlY3Qgd2lkdGg9IjE2IiBoZWlnaHQ9IjE2Ij48L3JlY3Q+PC9jbGlwUGF0aD48L2RlZnM+PC9zdmc+") center center / contain no-repeat;
        }
        .st-emotion-cache-105rmjc {
            background: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDE2IDE2IiBmaWxsPSJjdXJyZW50Q29sb3IiIGNvbG9yPSIjMzEzMzNGIj48ZyBjbGlwLXBhdGg9InVybCgjY2xpcDBfNzMwXzMxMjMpIj48cGF0aCBkPSJNMiAxMS42Mzk3VjEzLjY2NjRDMiAxMy44NTMgMi4xNDY2NyAxMy45OTk3IDIuMzMzMzMgMTMuOTk5N0g0LjM2QzQuNDQ2NjcgMTMuOTk5NyA0LjUzMzMzIDEzLjk2NjQgNC41OTMzMyAxMy44OTk3TDExLjg3MzMgNi42MjYzOEw5LjM3MzMzIDQuMTI2MzhMMi4xIDExLjM5OTdDMi4wMzMzMyAxMS40NjY0IDIgMTEuNTQ2NCAyIDExLjYzOTdaTTEzLjgwNjcgNC42OTMwNUMxNC4wNjY3IDQuNDMzMDUgMTQuMDY2NyA0LjAxMzA1IDEzLjgwNjcgMy43NTMwNUwxMi4yNDY3IDIuMTkzMDVDMTEuOTg2NyAxLjkzMzA1IDExLjU2NjcgMS45MzMwNSAxMS4zMDY3IDIuMTkzMDVMMTAuMDg2NyAzLjQxMzA1TDEyLjU4NjcgNS45MTMwNUwxMy44MDY3IDQuNjkzMDVWNC42OTMwNVoiPjwvcGF0aD48L2c+PGRlZnM+PGNsaXBQYXRoIGlkPSJjbGlwMF83MzBfMzEyMyI+PHJlY3Qgd2lkdGg9IjE2IiBoZWlnaHQ9IjE2IiBmaWxsPSJ3aGl0ZSI+PC9yZWN0PjwvY2xpcFBhdGg+PC9kZWZzPjwvc3ZnPg==") center center / contain no-repeat;
        }
        .st-emotion-cache-q16mip {
            background: url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0iY3VycmVudENvbG9yIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGNvbG9yPSIjMzEzMzNGIj48cGF0aCBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGNsaXAtcnVsZT0iZXZlbm9kZCIgZD0iTTguMDA2NjIgMC4zNTAwMDZDMy41NzkxNyAwLjM1MDAwNiAwIDMuODU1NCAwIDguMTkyMDZDMCAxMS42NTg2IDIuMjkzMjkgMTQuNTkyOSA1LjQ3NDcgMTUuNjMxNUM1Ljg3MjQ2IDE1LjcwOTUgNi4wMTgxNiAxNS40NjI3IDYuMDE4MTYgMTUuMjU1MUM2LjAxODE2IDE1LjA3MzMgNi4wMDUwNSAxNC40NTAxIDYuMDA1MDUgMTMuODAwOUMzLjc3NzggMTQuMjY4MyAzLjMxMzk5IDEyLjg2NiAzLjMxMzk5IDEyLjg2NkMyLjk1NjA2IDExLjk1NzIgMi40MjU3MiAxMS43MjM2IDIuNDI1NzIgMTEuNzIzNkMxLjY5Njc0IDExLjI0MzIgMi40Nzg4MiAxMS4yNDMyIDIuNDc4ODIgMTEuMjQzMkMzLjI4NzQ0IDExLjI5NTEgMy43MTE3NSAxMi4wNDgyIDMuNzExNzUgMTIuMDQ4MkM0LjQyNzQ1IDEzLjI0MjUgNS41ODA3NCAxMi45MDUxIDYuMDQ0NzEgMTIuNjk3M0M2LjExMDkyIDEyLjE5MDkgNi4zMjMxNSAxMS44NDA0IDYuNTQ4NSAxMS42NDU3QzQuNzcyMTEgMTEuNDYzOSAyLjkwMzEyIDEwLjc4ODggMi45MDMxMiA3Ljc3NjUxQzIuOTAzMTIgNi45MTk2IDMuMjIxMDcgNi4yMTg1MiAzLjcyNDg2IDUuNjczMjdDMy42NDUzOCA1LjQ3ODU2IDMuMzY2OTMgNC42NzM0NCAzLjgwNDUxIDMuNTk1ODRDMy44MDQ1MSAzLjU5NTg0IDQuNDgwNTUgMy4zODgwNyA2LjAwNDg4IDQuNDAwODFDNi42NTc1IDQuMjI5MTUgNy4zMzA1NCA0LjE0MTgzIDguMDA2NjIgNC4xNDEwOUM4LjY4MjY2IDQuMTQxMDkgOS4zNzE4MSA0LjIzMjA3IDEwLjAwODIgNC40MDA4MUMxMS41MzI3IDMuMzg4MDcgMTIuMjA4NyAzLjU5NTg0IDEyLjIwODcgMy41OTU4NEMxMi42NDYzIDQuNjczNDQgMTIuMzY3NyA1LjQ3ODU2IDEyLjI4ODIgNS42NzMyN0MxMi44MDUzIDYuMjE4NTIgMTMuMTEwMSA2LjkxOTYgMTMuMTEwMSA3Ljc3NjUxQzEzLjExMDEgMTAuNzg4OCAxMS4yNDExIDExLjQ1MDggOS40NTE0NiAxMS42NDU3QzkuNzQzMTggMTEuODkyMyA5Ljk5NDkyIDEyLjM1OTcgOS45OTQ5MiAxMy4wOTk4QzkuOTk0OTIgMTQuMTUxNCA5Ljk4MTgxIDE0Ljk5NTQgOS45ODE4MSAxNS4yNTVDOS45ODE4MSAxNS40NjI3IDEwLjEyNzcgMTUuNzA5NSAxMC41MjUzIDE1LjYzMTZDMTMuNzA2NyAxNC41OTI4IDE2IDExLjY1ODYgMTYgOC4xOTIwNkMxNi4wMTMxIDMuODU1NCAxMi40MjA4IDAuMzUwMDA2IDguMDA2NjIgMC4zNTAwMDZaIj48L3BhdGg+PC9zdmc+") center center / contain no-repeat;
        }
        .st-b6 {
            color: black;
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
            margin-top: 0px;
            margin-bottom: 0px;
            
            position: relative;
            top: 30px;
            z-index: 1;
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
            width: 450px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0 auto;
            overflow-x: auto;
            white-space: nowrap;
            
            position: relative;
            top: 53px;
            z-index: 1;
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
        }.spacing-50px {
            margin-bottom: 50px;
        }
        
        
        /* 버튼 스타일 변경 */
        button[kind="secondary"] {
            background-color: #ff8015 !important;
            color: #ffffff;
            border: none;
            border-radius: 20px;
            height: 35px;
            min-height: 10px;
        }
        
        div [data-testid="stButton"] {
            display: flex;
            justify-content: flex-end;
            margin: 10px;
            padding-right: 70px;
        }
        
        
        /* 하단 채팅모양 */
        .box_chatshape {
            background-color: white;
            border-radius: 25px;
            height: 50px;
            width: 700px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0 auto;
            padding-right: 80px;
            overflow-x: auto;
            white-space: nowrap;
            font-size: 0.9em;
            
            position: relative;
            top: 52px;
            z-index: 0;
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

        # 선택한 옵션은 selected_date, 이를 요일로 변환해 selected_weekday에 저장
        if date_option == "날짜 선택":
            weekdays = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
            selected_date = st.date_input("")
            st.session_state.selected_date = selected_date
            selected_weekday = weekdays[selected_date.weekday()]
        # 선택안함 시 빈칸으로 저장
        else:
            selected_weekday = None
        st.session_state.selected_weekday = selected_weekday

    # 시간대 선택 및 저장, 선택 안함 시 빈칸
    with col2:
        st.markdown("<div class='custom-label'>시간대를 선택해주세요.</div>", unsafe_allow_html=True)
        time_slot = st.selectbox(
            "", 
            ("선택 안함", "아침", "점심", "오후", "저녁", "밤")
        )
        if time_slot == "선택 안함":
            time_slot = ""
        st.session_state.time_slot = time_slot

    # 인원수 선택 및 저장, 선택 안함 시 빈칸
    with col3:
        st.markdown("<div class='custom-label'>인원수를 선택해주세요.</div>", unsafe_allow_html=True)
        members_num = st.selectbox(
            "", 
            ("선택 안함", "혼자", "2명", "3명", "4명 이상")
        )
        if members_num == "선택 안함":
            members_num = ""
        st.session_state.members_num = members_num


    # 새 박스를 추가
    st.markdown(
        """
        <div class="box-2">
            <h3>2. 방문 목적이 무엇인가요?</h3>
        </div>
        """,
        unsafe_allow_html=True
    )


    # 방문목적 선택 및 저장, 선택 안함 시 빈칸 : 중앙에 selectbox를 배치
    col_center = st.columns([1, 1, 1])
    with col_center[1]:
        visit_purpose = st.selectbox(
            "",
            ("선택 안함", "식사", "카페/디저트")
        )
        st.session_state.visit_purpose = visit_purpose
        

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
        
    # 선택된 지역 텍스트를 위한 placeholder 생성
    selected_region_text = st.empty()

        
    # 선택 초기화 버튼 클릭 시 선택된 지역 초기화
    if st.button("↺"):
        st.session_state.selected_regions = []
        st.session_state.selected_regions.append('reset')
        
    
    # 제주도 중심 좌표
    jeju_center = [33.38, 126.6] # 기존 33.4996, 126.5312

    # mapbox_token = st.secrets["MAPBOX_API_KEY"]
    mapbox_token = mapbox_key

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
    
    # 선택된 지역 이름을 처리        
    def selected_region_format(region): # 제주특별자치도 서귀포시 남원읍
        region_parts = region.split(' ')
        if region_parts[0] == "제주특별자치도" and len(region_parts) >= 3:
            return region_parts[1] + " " + region_parts[2]
        else:
            return region
        
    def display_format(region): # 서귀포시 남원읍, 제주시 (제주특별자치도 북부)
        region_parts = region.split(' ')
        if len(region_parts) == 2:
            return region_parts[1]
        else:
            return region_parts[0]    

    # 선택한 지역을 가져오기
    if st_data and st_data.get('last_active_drawing'):
        selected_region = st_data['last_active_drawing']['properties']['adm_nm']

        # 지역이 이미 선택된 리스트에 없으면 추가
        if selected_region_format(selected_region) not in st.session_state.selected_regions:
            st.session_state.selected_regions.append(selected_region_format(selected_region))
            
    
    st.session_state.selected_regions = [i for i in st.session_state.selected_regions]
        
    if st.session_state.selected_regions:
        if st.session_state.selected_regions[0] == 'reset':
            st.session_state.selected_regions = st.session_state.selected_regions[2:]
            
        
    selected_regions_display = ", ".join([display_format(region) for region in st.session_state.selected_regions])

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
        <div class="box_chatshape">
            감사합니다! 이제&nbsp<span class="text-bold">제주의 멋진 곳</span>을 추천해드리겠습니다☺️ 오른쪽 버튼을 두 번 눌러주세요&nbsp→
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if st.button("채팅 시작"):
        go_to_next_page()
        
    st.markdown('<div class="spacing-50px"></div>', unsafe_allow_html=True)



####### 두 번째 페이지 #######

# 변수 : selected_date, time_slot, members_num, visit_purpose, selected_regions(리스트) 
# -time_slot : "선택 안함", "아침", "점심", "오후", "저녁", "밤"
# -members_num : "선택 안함", "혼자", "2명", "3명", "4명 이상"
# -visit_purpose : "선택안함", "식사" "카페/디저트"
# -prompt : 사용자 input


elif st.session_state.page == 'next_page':
    
    # GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    
    # 프로필 이미지 설정
    assistant_avatar = "https://github.com/gina261/bigcontest_genAI/blob/main/images/chatbot_assistant.png?raw=true"
    user_avatar = "https://github.com/gina261/bigcontest_genAI/blob/main/images/chatbot_user.png?raw=true"
    
    # 기본 배경 설정
    st.markdown(
        """
        <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        
        /* Streamlit 전체 페이지의 배경을 변경하기 위한 설정 */
        .stApp {
            background-color: #ffefcc;
            font-family: 'Pretendard', sans-serif;
            color: black !important; /* 기본 텍스트 색상 */
        }
        /* 다크모드 상단바 */
        .st-emotion-cache-h4xjwg {
            background: #ffffff;
        }
        .st-emotion-cache-kd13nv {
            background: url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0iY3VycmVudENvbG9yIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGNvbG9yPSIjMzEzMzNGIj48ZyBjbGlwLXBhdGg9InVybCgjY2xpcDBfM18yKSI+PHBhdGggZD0iTTE0LjcwMjYgNS41MjAzN0wxMC40NjEyIDUuMTM1NDJMOC44MDQ5NSAxLjA1NjhDOC41MDcwMSAwLjMxNDQgNy40OTA0NCAwLjMxNDQgNy4xOTI1MSAxLjA1NjhMNS41MzYyNCA1LjE0NDU5TDEuMzAzNTYgNS41MjAzN0MwLjUzMjM4NyA1LjU4NDUzIDAuMjE2OTA4IDYuNTkyNzMgMC44MDQwNSA3LjEyNDMxTDQuMDIwMTggMTAuMDM4OUwzLjA1NjIyIDE0LjM2NUMyLjg4MDk1IDE1LjE1MzIgMy42OTU5NCAxNS43NzY1IDQuMzYxOTUgMTUuMzU0OUw3Ljk5ODY5IDEzLjA2MzZMMTEuNjM1NSAxNS4zNjQxQzEyLjMwMTUgMTUuNzg1NyAxMy4xMTY1IDE1LjE2MjQgMTIuOTQxMiAxNC4zNzQyTDExLjk3NzMgMTAuMDM4OUwxNS4xOTM0IDcuMTI0MzFDMTUuNzgwNSA2LjU5MjczIDE1LjQ3MzggNS41ODQ1MyAxNC43MDI2IDUuNTIwMzdaTTcuOTk4NjkgMTEuMzQ5Nkw0LjcwMzcyIDEzLjQzMDFMNS41ODAwNSA5LjUwNzMxTDIuNjcwNjMgNi44Njc2OUw2LjUwODk2IDYuNTE5NEw3Ljk5ODY5IDIuODI1NzNMOS40OTcyNiA2LjUyODU3TDEzLjMzNTYgNi44NzY4N0wxMC40MjYxIDkuNTE2NUwxMS4zMDI1IDEzLjQzOTNMNy45OTg2OSAxMS4zNDk2WiI+PC9wYXRoPjwvZz48ZGVmcz48Y2xpcFBhdGggaWQ9ImNsaXAwXzNfMiI+PHJlY3Qgd2lkdGg9IjE2IiBoZWlnaHQ9IjE2Ij48L3JlY3Q+PC9jbGlwUGF0aD48L2RlZnM+PC9zdmc+") center center / contain no-repeat;
        }
        .st-emotion-cache-105rmjc {
            background: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDE2IDE2IiBmaWxsPSJjdXJyZW50Q29sb3IiIGNvbG9yPSIjMzEzMzNGIj48ZyBjbGlwLXBhdGg9InVybCgjY2xpcDBfNzMwXzMxMjMpIj48cGF0aCBkPSJNMiAxMS42Mzk3VjEzLjY2NjRDMiAxMy44NTMgMi4xNDY2NyAxMy45OTk3IDIuMzMzMzMgMTMuOTk5N0g0LjM2QzQuNDQ2NjcgMTMuOTk5NyA0LjUzMzMzIDEzLjk2NjQgNC41OTMzMyAxMy44OTk3TDExLjg3MzMgNi42MjYzOEw5LjM3MzMzIDQuMTI2MzhMMi4xIDExLjM5OTdDMi4wMzMzMyAxMS40NjY0IDIgMTEuNTQ2NCAyIDExLjYzOTdaTTEzLjgwNjcgNC42OTMwNUMxNC4wNjY3IDQuNDMzMDUgMTQuMDY2NyA0LjAxMzA1IDEzLjgwNjcgMy43NTMwNUwxMi4yNDY3IDIuMTkzMDVDMTEuOTg2NyAxLjkzMzA1IDExLjU2NjcgMS45MzMwNSAxMS4zMDY3IDIuMTkzMDVMMTAuMDg2NyAzLjQxMzA1TDEyLjU4NjcgNS45MTMwNUwxMy44MDY3IDQuNjkzMDVWNC42OTMwNVoiPjwvcGF0aD48L2c+PGRlZnM+PGNsaXBQYXRoIGlkPSJjbGlwMF83MzBfMzEyMyI+PHJlY3Qgd2lkdGg9IjE2IiBoZWlnaHQ9IjE2IiBmaWxsPSJ3aGl0ZSI+PC9yZWN0PjwvY2xpcFBhdGg+PC9kZWZzPjwvc3ZnPg==") center center / contain no-repeat;
        }
        .st-emotion-cache-q16mip {
            background: url("data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0iY3VycmVudENvbG9yIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGNvbG9yPSIjMzEzMzNGIj48cGF0aCBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGNsaXAtcnVsZT0iZXZlbm9kZCIgZD0iTTguMDA2NjIgMC4zNTAwMDZDMy41NzkxNyAwLjM1MDAwNiAwIDMuODU1NCAwIDguMTkyMDZDMCAxMS42NTg2IDIuMjkzMjkgMTQuNTkyOSA1LjQ3NDcgMTUuNjMxNUM1Ljg3MjQ2IDE1LjcwOTUgNi4wMTgxNiAxNS40NjI3IDYuMDE4MTYgMTUuMjU1MUM2LjAxODE2IDE1LjA3MzMgNi4wMDUwNSAxNC40NTAxIDYuMDA1MDUgMTMuODAwOUMzLjc3NzggMTQuMjY4MyAzLjMxMzk5IDEyLjg2NiAzLjMxMzk5IDEyLjg2NkMyLjk1NjA2IDExLjk1NzIgMi40MjU3MiAxMS43MjM2IDIuNDI1NzIgMTEuNzIzNkMxLjY5Njc0IDExLjI0MzIgMi40Nzg4MiAxMS4yNDMyIDIuNDc4ODIgMTEuMjQzMkMzLjI4NzQ0IDExLjI5NTEgMy43MTE3NSAxMi4wNDgyIDMuNzExNzUgMTIuMDQ4MkM0LjQyNzQ1IDEzLjI0MjUgNS41ODA3NCAxMi45MDUxIDYuMDQ0NzEgMTIuNjk3M0M2LjExMDkyIDEyLjE5MDkgNi4zMjMxNSAxMS44NDA0IDYuNTQ4NSAxMS42NDU3QzQuNzcyMTEgMTEuNDYzOSAyLjkwMzEyIDEwLjc4ODggMi45MDMxMiA3Ljc3NjUxQzIuOTAzMTIgNi45MTk2IDMuMjIxMDcgNi4yMTg1MiAzLjcyNDg2IDUuNjczMjdDMy42NDUzOCA1LjQ3ODU2IDMuMzY2OTMgNC42NzM0NCAzLjgwNDUxIDMuNTk1ODRDMy44MDQ1MSAzLjU5NTg0IDQuNDgwNTUgMy4zODgwNyA2LjAwNDg4IDQuNDAwODFDNi42NTc1IDQuMjI5MTUgNy4zMzA1NCA0LjE0MTgzIDguMDA2NjIgNC4xNDEwOUM4LjY4MjY2IDQuMTQxMDkgOS4zNzE4MSA0LjIzMjA3IDEwLjAwODIgNC40MDA4MUMxMS41MzI3IDMuMzg4MDcgMTIuMjA4NyAzLjU5NTg0IDEyLjIwODcgMy41OTU4NEMxMi42NDYzIDQuNjczNDQgMTIuMzY3NyA1LjQ3ODU2IDEyLjI4ODIgNS42NzMyN0MxMi44MDUzIDYuMjE4NTIgMTMuMTEwMSA2LjkxOTYgMTMuMTEwMSA3Ljc3NjUxQzEzLjExMDEgMTAuNzg4OCAxMS4yNDExIDExLjQ1MDggOS40NTE0NiAxMS42NDU3QzkuNzQzMTggMTEuODkyMyA5Ljk5NDkyIDEyLjM1OTcgOS45OTQ5MiAxMy4wOTk4QzkuOTk0OTIgMTQuMTUxNCA5Ljk4MTgxIDE0Ljk5NTQgOS45ODE4MSAxNS4yNTVDOS45ODE4MSAxNS40NjI3IDEwLjEyNzcgMTUuNzA5NSAxMC41MjUzIDE1LjYzMTZDMTMuNzA2NyAxNC41OTI4IDE2IDExLjY1ODYgMTYgOC4xOTIwNkMxNi4wMTMxIDMuODU1NCAxMi40MjA4IDAuMzUwMDA2IDguMDA2NjIgMC4zNTAwMDZaIj48L3BhdGg+PC9zdmc+") center center / contain no-repeat;
        }
        
        /* 아바타 이미지 (둘 다) */
        div[data-testid="stChatMessage"] > img {
            width: 50px !important;
            height: 60px !important;
            object-fit: cover;  /* 이미지 비율 유지하면서 크기 조정 */
        }
        
        /* User 아바타 이미지 */
        div[data-testid="stChatMessage"] > img[alt="user avatar"] {
            order: 1;
        }
        
        div[data-testid="stChatMessage"] {
            display: flex;
            align-items: flex-end;
            background-color: #feefcc;
        }
        
        /* 메시지 내용 왼쪽에 배치 */
        div[data-testid="stChatMessage"] > div[data-testid="stChatMessageContent"] {
            order: 0;  /* 메시지를 왼쪽에 배치 - User만*/
            margin-right: 20px;  /* 아바타와 텍스트 사이 간격 */
            margin-left: 20px;
        }
        
        /* assistant 메시지 스타일 */
        div[data-testid="stChatMessageContent"][aria-label="Chat message from assistant"] {
            background-color: #ffffff;
            padding: 10px 20px;
            border-radius: 15px;
            width: auto;
            word-wrap: break-word;
            max-width: 100%;
            justify-contet: center;
            color: #000000;
        }
        
        /* User 메시지 스타일 */
        div[data-testid="stChatMessageContent"][aria-label="Chat message from user"] {
            background-color: #ffddaf;
            padding: 10px 20px;
            border-radius: 15px;
            width: auto;
            word-wrap: break-word;
            display: 100%;
            justify-content: center;
            color: #000000;
        }
        
        
        /* 채팅 입력창 스타일 */
        /* 입력창 배경 */
        div [class="st-emotion-cache-128upt6 ea3mdgi6"] {
            background-color: #ffefcc !important;
        }
        div [class="st-emotion-cache-hzygls ea3mdgi6"] {
            background-color: #ffefcc !important;
        }        
        
        div [data-baseweb="base-input"] {
            font-family: 'Pretendard', sans-serif;
        }
        div [data-baseweb="textarea"] {
            background-color: #ffffff;
            border-color: #ffffff;
            border-radius: 30px;
            padding: 3px 15px;
        }
        textarea[data-testid="stChatInputTextArea"]{
            color: #000000;
            caret-color: #000000;
        }
        div [data-testid="stChatInput"] {
            background-color: #ffefcc;
        }
        div [data-testid="stBottomBlockContainer"] {
            padding: 1rem 1rem 30px;
        }
        
        /* 뒤로가기 버튼 */
        button[kind="secondary"] {
            background-color: #feefcc !important;
            color: #f7a660;
            border: none;
            border-radius: 20px;
            height: 35px;
            min-height: 10px;
        }
        button[kind="secondary"]:hover {
            color: #ee8124;
        }
        div [data-testid="stButton"] {
            position: fixed;
            top: 80px;
            left: 10px;
            margin: 10px;
            padding-right: 70px;
            z-index: 1000;
        }
        
        /* 사용자 선택 옵션 expander */
        div [data-testid="stExpander"] {
            position: fixed;
            top: 150px;
            left: 20px;
            width: 250px;
        }
        .st-emotion-cache-1h9usn1 {
            border-style: none;
        }
        
        /* expander 스크롤 */
        div [data-testid="stExpanderDetails"] {
            height: 400px;
            overflow: scroll;
        }
        
        /* expander 글씨체1 */
        .expander-detail {
            font-size: 0.7em;
            font-weight: 100;
            font-family: 'Pretendard', sans-serif;
        }
        
        .expander-title {
            font-size: 0.9em;
            font-weight: 300;
            font-family: 'Pretendard', sans-serif;
        }
        
        /* expander 라벨 영역 없애기 */
        .st-emotion-cache-ue6h4q {
            min-height: 5px;
        }
        .st-emotion-cache-1qg05tj {
            min-height: 5px;
        }
        
        /* expander 옵션 선택바 */
        .st-emotion-cache-p5msec {
            width: 55%;
        }
        /* hover 색 */
        .st-emotion-cache-p5msec:hover {
            color: #ee8124;
        }
        .st-emotion-cache-p5msec:hover svg {
            fill: #ee8124;
        }
        
        .expander-border {
            position: fixed;
            top: 155px;
            left: 22px;
            width: 130px;
            height: 35px;
            background-color: #e5dcc9;
            border: none;
            border-radius: 10px;
            padding: 10px;
            box-sizing: border-box;
        }
        
        /* 지역 선택 박스 색상 */
        .st-e9 {
            background-color: #ee8124;
        }
        
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # session_state 초기화
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "오늘의 기분이나 상황을 입력해주세요. 그에 맞는 제주의 멋진 곳을 추천해드립니다."}]
    
    
    # 채팅 화면 초기화 함수
    def clear_chat_history():
        st.session_state.messages = [{"role": "assistant", "content": "오늘의 기분이나 상황을 입력해주세요. 그에 맞는 제주의 멋진 곳을 추천해드립니다."}]
    
    # 채팅 화면 표시
    for message in st.session_state.messages:
        avatar = user_avatar if message["role"] == "user" else assistant_avatar
        with st.chat_message(message["role"], avatar=avatar):
            st.write(message["content"])

 
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=user_avatar):
            st.write(prompt)
            
           
    # 사용자가 새로운 메시지를 입력한 후 응답 생성
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant", avatar=assistant_avatar):
            # (Step 1) 1번, 2번 중 어느 질문인지 반환 [첫번째 gemini 호출]
            which_csv = detect_emotion_and_context(prompt)
            print("이 질문은" + which_csv)

            with st.spinner("Thinking..."):
                # (Step 2) 2번 질문일 경우 (추천형 질문)
                if int(which_csv[0]) == 2:
                    # (2-1) 고정질문 (방문지역, 방문목적) 기준으로 필터링
                    fixed_filtered = filter_fixed_address_purpose(st.session_state.selected_regions, st.session_state.visit_purpose, text2_df)

                    # (2-2) 고정질문 (날짜, 시간, 인원수) 기준으로 사용자 질문 수정
                    weekdays = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
                    
                    if st.session_state.selected_date == None:
                        st.session_state.selected_weekday = ""
                    else:
                        st.session_state.selected_weekday = weekdays[st.session_state.selected_date.weekday()]
                    
                    print(f'날짜,시간,인원수: {st.session_state.selected_weekday}, {st.session_state.time_slot}, {st.session_state.members_num}')
                    prompt = filter_fixed_datetime_members(st.session_state.selected_weekday, st.session_state.time_slot, st.session_state.members_num, prompt)

                    # (2-3) FAISS 검색을 통해 유사도가 높은 15가지 레스토랑 추출
                    top_15 = text2faiss(prompt, fixed_filtered) 
                    print(f'faiss 추출 개수: {len(top_15)}')
                    print(f'faiss 추천된 데이터 : {top_15["restaurant_name"]}')

                    # (2-4) gemini 호출을 통해 추출된 15개의 레스토랑 중 추천 [두번째 gemini 호출]
                    response = recommend_restaurant_from_subset(prompt, top_15)
                    print(response)

                # (Step 3) 1번 질문일 경우 (검색형 질문)
                else: 
                    # (3-1) 신한카드 데이터에 고정질문 (방문지역, 방문 목적 기준으로)
                    print(f'고정질문: {st.session_state.selected_regions, st.session_state.visit_purpose}')

                    if st.session_state.selected_regions == []:
                        filtered_df = df.copy()
                    else:
                        filtered_df = df[df['address_map'].apply(lambda x: isinstance(x, str) and any(addr in x for addr in st.session_state.selected_regions))]
                        print(f'지역 필터링 완료, 길이: {len(filtered_df)}')

                    if st.session_state.visit_purpose != '선택 안함':
                        filtered_df = filtered_df[filtered_df['목적'] == st.session_state.visit_purpose]


                    # (3-1) sql 쿼리 반환 [두번째 gemini 호출]
                    sql_query = convert_question_to_sql(which_csv)
                    print(f"Generated SQL Query: {sql_query}")
                    # (2-2) sql 쿼리 적용 및 결과 반환

                    sql_results = execute_sql_query_on_df(sql_query, filtered_df)

                    # (2-3) 반환된 데이터가 없을 시 faiss 적용, 있다면 그대로 gemini 호출 [세번째 gemini 호출]

                    if sql_results.empty:
                        print("SQL query failed or returned no results. Falling back to FAISS.")

                        filtered_fix= filter_fixed_address_purpose_text1(st.session_state.selected_regions, st.session_state.visit_purpose, df)
                        
                        embeddings_path = config['faiss']['embeddings_path'] 

                        embeddings = np.load(embeddings_path)
                        response = generate_response_with_faiss(prompt, filtered_fix, embeddings, model, embed_text)
                        print(response)
                    else:
                        response = generate_gemini_response_from_results(sql_results, prompt)
                        print(response)

            
                placeholder = st.empty()
                full_response = ''
                
                # 만약 response가 GenerateContentResponse 객체라면, 문자열로 변환하여 사용합니다.
                if isinstance(response, str):
                    full_response = response
                else:
                    full_response = response.text # response 객체에서 텍스트 부분 추출
                
                placeholder.markdown(full_response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)
        

    # 뒤로가기 버튼 클릭 시 초기화 함수
    def go_to_previous():
        # 메인 페이지로 이동
        st.session_state.page = 'main'
        st.session_state.selected_regions = []
        st.session_state.selected_date = None
        st.session_state.messages = [{"role": "assistant", "content": "오늘의 기분이나 상황을 입력해주세요. 그에 맞는 제주의 멋진 곳을 추천해드립니다."}]  # 채팅 기록 초기화
        
        # 대화 기록 초기화
        # clear_chat_history()

    # 뒤로가기 버튼 생성
    if st.button("⇦ 뒤로"):
        go_to_previous()



    ####### 옵션 수정 expander 생성 #######
    st.markdown(
        """
        <div class="expander-border">
        
        </div>
        """,
        unsafe_allow_html=True
    )
    
    with st.expander("⚙️ &nbsp;&nbsp;고정 질문", expanded=False):
        st.markdown(
            """
            <div class="expander-detail">
                선택한 옵션을 확인하거나 수정할 수 있습니다.
            </div>
        
            <div class="expander-title">
                날짜
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if 'selected_date' not in st.session_state:
            st.session_state.selected_date = None
        if st.session_state.selected_date != None:
            date_option = st.selectbox(
                "", 
                ["선택 안함", "날짜 선택"],
                index=1
            )
        else:
            date_option = st.selectbox(
                "",
                ["선택 안함", "날짜 선택"],
                index=0
            )
        if date_option == "날짜 선택":
            st.session_state.selected_date = st.date_input("", st.session_state.selected_date)
        else:
            st.session_state.selected_date = None
            
            
        st.markdown(
            """
            <div class="expander-title">
                시간대
            </div>
            """,
            unsafe_allow_html=True
        )
        # 시간대 확인 및 수정
        if st.session_state.time_slot == "":
            st.session_state.time_slot = "선택 안함"

        time_slot = st.selectbox(
            "",
            ("선택 안함", "아침", "점심", "오후", "저녁", "밤"),
            index=["선택 안함", "아침", "점심", "오후", "저녁", "밤"].index(st.session_state.time_slot)
        )
        if time_slot == "선택 안함":
            time_slot = ""
        st.session_state.time_slot = time_slot
        
        
        st.markdown(
            """
            <div class="expander-title">
                인원수
            </div>
            """,
            unsafe_allow_html=True
        )
        # 인원수 확인 및 수정
        if st.session_state.members_num == "":
            st.session_state.members_num = "선택 안함"
        
        members_num = st.selectbox(
            "",
            ("선택 안함", "혼자", "2명", "3명", "4명 이상"),
            index=["선택 안함", "혼자", "2명", "3명", "4명 이상"].index(st.session_state.members_num)
        )
        if members_num == "선택 안함":
            members_num = ""
        st.session_state.members_num = members_num
        
        st.markdown(
            """
            <div class="expander-title">
                방문 목적
            </div>
            """,
            unsafe_allow_html=True
        )
        # 방문 목적 확인 및 수정
        if st.session_state.visit_purpose == "":
            st.session_state.visit_purpose = "선택 안함"
            
        st.session_state.visit_purpose = st.selectbox(
            "",
            ("선택 안함", "식사", "카페/디저트"),
            index=["선택 안함", "식사", "카페/디저트"].index(st.session_state.visit_purpose)
        )
        
        
        st.markdown(
            """
            <div class="expander-title">
                지역
            </div>
            """,
            unsafe_allow_html=True
        )
        # 지역 확인 및 수정
        regions_list = ["서귀포시 (제주특별자치도 남부)", "서귀포시 남원읍", "서귀포시 대정읍", "서귀포시 성산읍", "서귀포시 안덕면", "서귀포시 표선면", "제주시 (제주특별자치도 북부)", "제주시 구좌읍", "제주시 애월읍", "제주시 우도면", "제주시 조천읍", "제주시 한경면", "제주시 한림읍"]
        tmp_selected = st.multiselect(
            "",
            regions_list,
            default=st.session_state.selected_regions
        )
        
        st.session_state.selected_regions = tmp_selected