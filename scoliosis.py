import streamlit as st
import pandas as pd
import plotly.express as px
import cv2
import numpy as np
from datetime import datetime
import os
from PIL import Image
import io

from database import Database
from image_processor import ImageProcessor
from exercise_guide import ExerciseGuide

# 전역 변수 초기화
if 'db' not in st.session_state:
    st.session_state.db = Database()
if 'image_processor' not in st.session_state:
    st.session_state.image_processor = ImageProcessor()
if 'exercise_guide' not in st.session_state:
    st.session_state.exercise_guide = ExerciseGuide()
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# 페이지 설정
st.set_page_config(
    page_title="척추측만증 자가진단",
    page_icon="🏥",
    layout="wide"
)

def resize_image(image, max_width=800):
    """이미지 크기를 조정하는 함수"""
    width, height = image.size
    if width > max_width:
        ratio = max_width / width
        new_height = int(height * ratio)
        return image.resize((max_width, new_height), Image.Resampling.LANCZOS)
    return image

def get_exercise_shorts():
    """운동 관련 쇼츠 영상 정보를 가져오는 함수"""
    return [
        {
            "title": "척추측만증 개선을 위한 스트레칭",
            "url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "duration": "3:45",
            "trainer": "김트레이너"
        },
        {
            "title": "척추 정렬 운동 가이드",
            "url": "https://www.youtube.com/embed/9bZkp7q19f0",
            "thumbnail": "https://img.youtube.com/vi/9bZkp7q19f0/maxresdefault.jpg",
            "duration": "4:20",
            "trainer": "이트레이너"
        },
        {
            "title": "척추측만증 예방 운동",
            "url": "https://www.youtube.com/embed/JGwWNGJdvx8",
            "thumbnail": "https://img.youtube.com/vi/JGwWNGJdvx8/maxresdefault.jpg",
            "duration": "5:15",
            "trainer": "박트레이너"
        }
    ]

def login_page():
    st.title("척추측만증 자가진단")
    
    with st.form("login_form"):
        name = st.text_input("이름")
        age = st.number_input("나이", min_value=1, max_value=120)
        gender = st.selectbox("성별", ["남성", "여성"])
        
        submitted = st.form_submit_button("로그인")
        
        if submitted:
            if name and age and gender:
                user_id = st.session_state.db.add_user(name, age, gender)
                st.session_state.user_id = user_id
                st.success("로그인 성공!")
                return True
            else:
                st.error("모든 필드를 입력해주세요.")
    return False

def user_profile():
    st.sidebar.title("개인 정보")
    
    if st.session_state.user_id:
        user = st.session_state.db.get_user(st.session_state.user_id)
        if user:
            st.sidebar.write(f"**이름:** {user[1]}")
            st.sidebar.write(f"**나이:** {user[2]}")
            st.sidebar.write(f"**성별:** {user[3]}")
            
            with st.sidebar.expander("추가 정보 수정"):
                height = st.number_input("키 (cm)", value=float(user[4]) if user[4] else None, min_value=100.0, max_value=250.0)
                weight = st.number_input("몸무게 (kg)", value=float(user[5]) if user[5] else None, min_value=30.0, max_value=200.0)
                scoliosis_type = st.selectbox(
                    "척추측만증 형태",
                    ["C형", "S형", "복합형", "미확인"],
                    index=["C형", "S형", "복합형", "미확인"].index(user[6]) if user[6] else 3
                )
                
                if st.button("정보 업데이트"):
                    st.session_state.db.update_user(st.session_state.user_id, height, weight, scoliosis_type)
                    st.success("정보가 업데이트되었습니다!")
                    st.experimental_rerun()

# 사이드바 메뉴
def sidebar_menu():
    with st.sidebar:
        st.title("메뉴")
        menu = st.radio(
            "선택하세요",
            ["메인 대시보드", "자가진단", "운동 가이드", "기록 관리", "설정"]
        )
        return menu
    return None

# 메인 대시보드
def main_dashboard():
    st.title("척추측만증 자가진단")
    st.write("안녕하세요! 척추측만증 자가진단 웹 앱에 오신 것을 환영합니다.")
    
    if st.session_state.user_id:
        user = st.session_state.db.get_user(st.session_state.user_id)
        if user and user[6]:  # scoliosis_type이 있는 경우
            st.info(f"현재 진단된 척추측만증 형태: {user[6]}")
            if user[6] == "C형":
                st.write("C형 척추측만증은 한쪽으로만 휘어진 형태입니다. 주로 요추부에 발생하며, 운동과 스트레칭으로 개선이 가능합니다.")
            elif user[6] == "S형":
                st.write("S형 척추측만증은 상부와 하부가 반대 방향으로 휘어진 형태입니다. 정기적인 검사와 운동이 필요합니다.")
            elif user[6] == "복합형":
                st.write("복합형 척추측만증은 여러 부위에 걸쳐 휘어진 형태입니다. 전문의와 상담이 필요할 수 있습니다.")
    
    # 오늘의 통계
    col1, col2, col3 = st.columns(3)
    
    with col1:
        diagnoses = st.session_state.db.get_user_diagnoses(st.session_state.user_id) if st.session_state.user_id else []
        today = datetime.now().date()
        today_diagnoses = len([d for d in diagnoses if datetime.strptime(d[5], '%Y-%m-%d %H:%M:%S').date() == today])
        st.metric(label="오늘의 진단", value=f"{today_diagnoses}회")
    
    with col2:
        exercises = st.session_state.db.get_user_exercises(st.session_state.user_id) if st.session_state.user_id else []
        completed_exercises = len([e for e in exercises if e[3] and datetime.strptime(e[4], '%Y-%m-%d').date() == today])
        st.metric(label="운동 완료", value=f"{completed_exercises}회")
    
    with col3:
        if diagnoses:
            latest_curvature = diagnoses[0][3]
            progress = min(100, (latest_curvature / 0.5) * 100)
            st.metric(label="진행 상황", value=f"{progress:.1f}%")
        else:
            st.metric(label="진행 상황", value="0%")

# 자가진단 페이지
def self_diagnosis():
    st.title("자가진단")
    
    tab1, tab2 = st.tabs(["아담스 테스트", "기본 자세 체크"])
    
    with tab1:
        st.header("아담스 테스트")
        st.write("앞으로 굽혀서 등 사진을 업로드해주세요.")
        uploaded_file = st.file_uploader("사진 업로드", type=['jpg', 'jpeg', 'png'])
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            resized_image = resize_image(image)
            st.image(resized_image, caption="업로드된 이미지", use_container_width=True)
            
            if st.button("분석 시작"):
                with st.spinner("이미지를 분석중입니다..."):
                    curvature = st.session_state.image_processor.process_adams_test(image)
                    if curvature is not None:
                        st.success(f"분석 완료! 척추 곡률: {curvature:.2f}")
                        st.session_state.db.add_diagnosis(
                            st.session_state.user_id,
                            "adams_test",
                            curvature,
                            uploaded_file.name
                        )
                    else:
                        st.error("이미지 분석에 실패했습니다. 다시 시도해주세요.")
    
    with tab2:
        st.header("기본 자세 체크")
        st.write("기본 자세 체크를 위한 사진을 업로드해주세요.")
        uploaded_file = st.file_uploader("기본 자세 사진 업로드", type=['jpg', 'jpeg', 'png'])
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            resized_image = resize_image(image)
            st.image(resized_image, caption="업로드된 이미지", use_container_width=True)
            
            if st.button("자세 분석 시작"):
                with st.spinner("자세를 분석중입니다..."):
                    posture_data = st.session_state.image_processor.process_posture(image)
                    if posture_data:
                        st.success("분석 완료!")
                        st.write("분석 결과:")
                        st.write(f"- 어깨 높이 차이: {posture_data['shoulder_difference']:.2f}")
                        st.write(f"- 골반 기울기: {posture_data['hip_difference']:.2f}")
                        st.write(f"- 척추 정렬: {posture_data['spine_alignment']:.2f}")
                        
                        # 결과 저장
                        result = (posture_data['shoulder_difference'] + 
                                posture_data['hip_difference'] + 
                                posture_data['spine_alignment']) / 3
                        st.session_state.db.add_diagnosis(
                            st.session_state.user_id,
                            "posture_check",
                            result,
                            uploaded_file.name
                        )
                    else:
                        st.error("자세 분석에 실패했습니다. 다시 시도해주세요.")

# 운동 가이드 페이지
def exercise_guide():
    st.title("운동 가이드")
    
    if st.session_state.user_id:
        user = st.session_state.db.get_user(st.session_state.user_id)
        if user and user[6]:  # scoliosis_type이 있는 경우
            st.info(f"현재 진단된 척추측만증 형태: {user[6]}")
            if user[6] == "C형":
                st.write("C형 척추측만증에 맞는 운동을 추천해드립니다.")
            elif user[6] == "S형":
                st.write("S형 척추측만증에 맞는 운동을 추천해드립니다.")
            elif user[6] == "복합형":
                st.write("복합형 척추측만증에 맞는 운동을 추천해드립니다.")
    
    # 최근 진단 결과 가져오기
    diagnoses = st.session_state.db.get_user_diagnoses(st.session_state.user_id) if st.session_state.user_id else []
    if diagnoses:
        latest_curvature = diagnoses[0][3]
        st.write(f"최근 진단 결과에 따른 맞춤 운동을 추천해드립니다.")
        
        # 운동 프로그램 가져오기
        program = st.session_state.exercise_guide.get_exercise_program(latest_curvature, "30분")
        
        # 운동 프로그램 표시
        st.subheader("맞춤 운동 프로그램")
        for exercise in program:
            with st.expander(f"{exercise['name']} ({exercise['difficulty']})"):
                st.write(f"**설명:** {exercise['description']}")
                st.write(f"**소요 시간:** {exercise['duration']}")
                
                if st.button(f"{exercise['name']} 완료", key=exercise['name']):
                    st.session_state.db.add_exercise(
                        st.session_state.user_id,
                        exercise['name'],
                        True,
                        datetime.now().strftime('%Y-%m-%d')
                    )
                    st.success("운동이 완료되었습니다!")
        
        # 전문 트레이너 쇼츠 섹션
        st.subheader("전문 트레이너 운동 가이드")
        shorts = get_exercise_shorts()
        
        # 쇼츠를 3열로 표시
        cols = st.columns(3)
        for idx, short in enumerate(shorts):
            with cols[idx % 3]:
                st.markdown(f"""
                    <div style="border: 1px solid #ddd; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                        <img src="{short['thumbnail']}" style="width: 100%; border-radius: 5px;">
                        <h4 style="margin: 10px 0;">{short['title']}</h4>
                        <p style="color: #666;">트레이너: {short['trainer']}</p>
                        <p style="color: #666;">소요시간: {short['duration']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("영상 보기", key=f"video_{idx}"):
                    st.markdown(f"""
                        <iframe
                            width="100%"
                            height="315"
                            src="{short['url']}"
                            frameborder="0"
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                            allowfullscreen>
                        </iframe>
                    """, unsafe_allow_html=True)
    else:
        st.write("진단 결과가 없습니다. 자가진단을 먼저 진행해주세요.")

# 기록 관리 페이지
def record_management():
    st.title("진단 기록 관리")
    
    if st.session_state.user_id:
        # 진단 기록 가져오기
        diagnoses = st.session_state.db.get_user_diagnoses(st.session_state.user_id)
        if diagnoses:
            # 데이터프레임 생성
            df = pd.DataFrame(diagnoses, columns=['id', 'user_id', 'test_type', 'result', 'image_path', 'created_at'])
            
            # 날짜 형식 변환
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            # 그래프 생성
            fig = px.line(df, x='created_at', y='result', 
                         title='진단 결과 추이',
                         labels={'result': '측정값', 'created_at': '날짜'})
            st.plotly_chart(fig, use_container_width=True)
            
            # 데이터 테이블 표시
            st.write("상세 기록")
            st.dataframe(df)
            
            # PDF 리포트 생성 버튼
            if st.button("PDF 리포트 생성"):
                # PDF 생성 로직 추가 예정
                st.info("PDF 리포트 생성 기능은 추후 업데이트될 예정입니다.")
        else:
            st.write("아직 진단 기록이 없습니다.")
    else:
        st.write("로그인이 필요합니다.")

# 설정 페이지
def settings():
    st.title("설정")
    
    # 알림 설정
    notification_enabled = st.checkbox(
        "알림 활성화",
        value=True
    )
    
    # 테마 설정
    theme = st.selectbox(
        "테마",
        ["라이트", "다크"],
        index=0
    )
    
    if st.button("설정 저장"):
        st.success("설정이 저장되었습니다!")

# 메인 함수
def main():
    if not st.session_state.user_id:
        if not login_page():
            return
    
    user_profile()
    menu = sidebar_menu()
    
    if menu == "메인 대시보드":
        main_dashboard()
    elif menu == "자가진단":
        self_diagnosis()
    elif menu == "운동 가이드":
        exercise_guide()
    elif menu == "기록 관리":
        record_management()
    elif menu == "설정":
        settings()

if __name__ == "__main__":
    main()
