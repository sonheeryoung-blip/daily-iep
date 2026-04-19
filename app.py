import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="매일 기록하는 IEP", page_icon="💙", layout="wide")

# 스타일 설정
st.markdown("""
    <style>
    .main { background-color: #F8FBFF; }
    .student-card {
        background-color: white; padding: 15px; border-radius: 12px;
        border: 1px solid #B3E5FC; margin-bottom: 10px;
    }
    .goal-box {
        background-color: #F0F8FF; padding: 10px; border-radius: 8px;
        margin-bottom: 5px; border-left: 5px solid #4682B4;
    }
    </style>
    """, unsafe_allow_html=True)

if 'students' not in st.session_state:
    st.session_state.students = []

st.title("💙 매일 기록하는 IEP")

SPECIAL_AREAS = ["시각장애", "청각장애", "지적장애", "지체장애", "정서·행동장애", "자폐성장애", "의사소통장애", "학습장애", "건강장애", "발달지체"]
DEVELOPMENT_DOMAINS = ["인지", "의사소통", "운동성", "사회정서", "적응행동"]

tab1, tab2, tab3 = st.tabs(["📂 유아 관리", "📝 기록하기", "📊 월간 분석"])

# --- 📂 1. 유아 관리 탭 ---
with tab1:
    col_reg, col_list = st.columns([1, 1])
    
    with col_reg:
        st.subheader("✨ 새로운 유아 추가")
        with st.form("student_form", clear_on_submit=True):
            st.info("아이의 기본 정보와 최대 8개의 IEP 목표를 설정하세요.")
            name = st.text_input("아이 이름")
            class_name = st.text_input("통합학급")
            special_type = st.selectbox("특수교육대상 선정영역", SPECIAL_AREAS)
            welfare_card = st.text_input("복지카드 정보")
            
            st.write("---")
            st.write("🎯 **IEP 세부 목표 설정 (최대 8개)**")
            
            # 8개 목표 입력란 생성
            goals = []
            for i in range(1, 9):
                with st.expander(f"📍 목표 {i} 설정"):
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        d = st.selectbox(f"영역", DEVELOPMENT_DOMAINS, key=f"dom_{i}")
                    with c2:
                        t = st.text_input(f"세부내용", key=f"txt_{i}", placeholder="내용이 없으면 비워두세요")
                    goals.append({"영역": d, "내용": t})
            
            submitted = st.form_submit_button("등록 완료")
            if submitted and name:
                st.session_state.students.append({
                    "이름": name, "학급": class_name, "영역": special_type, "복지": welfare_card, "목표": goals
                })
                st.success(f"{name} 선생님 반 아이로 등록되었습니다!")
                st.rerun()

    with col_list:
        st.subheader("👥 우리 반 아이들 목록")
        if not st.session_state.students:
            st.info("왼쪽에서 아이를 등록해주세요.")
        else:
            for s in st.session_state.students:
                with st.expander(f"👤 {s['이름']} ({s['학급']})"):
                    st.write(f"**선정영역:** {s['영역']} | **복지:** {s['복지']}")
                    for i, g in enumerate(s['목표']):
                        if g['내용']:
                            st.markdown(f"<div class='goal-box'><b>목표 {i+1} ({g['영역']}):</b> {g['내용']}</div>", unsafe_allow_html=True)

# --- 📝 2. 기록하기 탭 ---
with tab2:
    if not st.session_state.students:
        st.warning("유아를 먼저 등록해주세요.")
    else:
        selected_name = st.selectbox("기록할 아이 선택", [s['이름'] for s in st.session_state.students])
        student = next(s for s in st.session_state.students if s['이름'] == selected_name)
        
        st.subheader(f"📊 {selected_name} 어린이 실시간 기록")
        for i, g in enumerate(student['목표']):
            if g['내용']:
                with st.container():
                    st.markdown(f"**[{g['영역']}] {g['내용']}**")
                    c1, c2, c3 = st.columns([1, 1, 2])
                    with c1:
                        st.button("➕ 수행", key=f"inc_{selected_name}_{i}")
                    with c2:
                        st.number_input("기준", 1, 20, 5, key=f"tar_{selected_name}_{i}")
                    with c3:
                        st.slider("성취도", 0, 100, 50, key=f"sld_{selected_name}_{i}")
                st.write("---")
        
        st.text_area("오늘의 누가기록 메모")
        st.button("🚀 데이터 전송 (구글 시트 연동 준비)")

# --- 📊 3. 월간 분석 탭 ---
with tab3:
    st.write("데이터 전송이 완료되면 실제 그래프가 활성화됩니다.")
