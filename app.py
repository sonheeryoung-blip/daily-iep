import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정 및 테마
st.set_page_config(page_title="매일 기록하는 IEP", page_icon="💙", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F8FBFF; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #E1F5FE;
        border-radius: 5px 5px 0px 0px;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #B3E5FC !important; font-weight: bold; }
    .student-card {
        background-color: white; padding: 20px; border-radius: 15px;
        border: 2px solid #B3E5FC; text-align: center; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 데이터 초기화 (임시 저장소)
if 'students' not in st.session_state:
    st.session_state.students = []

st.title("💙 매일 기록하는 IEP")

# 범주 설정
SPECIAL_AREAS = ["시각장애", "청각장애", "지적장애", "지체장애", "정서·행동장애", "자폐성장애", "의사소통장애", "학습장애", "건강장애", "발달지체"]
DEVELOPMENT_DOMAINS = ["인지", "의사소통", "운동성", "사회정서", "적응행동"]

tab1, tab2, tab3 = st.tabs(["📂 유아 관리", "📝 기록하기", "📊 월간 분석"])

# --- 📂 1. 유아 관리 탭 (여기에 추가 기능을 넣었습니다!) ---
with tab1:
    col_reg, col_list = st.columns([1, 1])
    
    with col_reg:
        st.subheader("✨ 새로운 유아 추가")
        with st.form("student_form", clear_on_submit=True):
            name = st.text_input("아이 이름")
            class_name = st.text_input("통합학급")
            special_type = st.selectbox("특수교육대상 선정영역", SPECIAL_AREAS)
            welfare_card = st.text_input("복지카드 정보")
            
            st.write("---")
            st.caption("🎯 IEP 목표 설정 (최대 2개)")
            g1_domain = st.selectbox("목표1 영역", DEVELOPMENT_DOMAINS)
            g1_text = st.text_input("목표1 세부내용")
            g2_domain = st.selectbox("목표2 영역", DEVELOPMENT_DOMAINS)
            g2_text = st.text_input("목표2 세부내용")
            
            submitted = st.form_submit_button("등록하기")
            if submitted and name:
                new_student = {
                    "이름": name, "학급": class_name, "영역": special_type, "복지": welfare_card,
                    "목표": [{"영역": g1_domain, "내용": g1_text}, {"영역": g2_domain, "내용": g2_text}]
                }
                st.session_state.students.append(new_student)
                st.success(f"{name} 등록 완료!")
                st.rerun()

    with col_list:
        st.subheader("👥 우리 반 아이들")
        if not st.session_state.students:
            st.info("왼쪽에서 아이를 먼저 등록해주세요.")
        else:
            for s in st.session_state.students:
                with st.expander(f"👤 {s['이름']} ({s['학급']})"):
                    st.write(f"**선정영역:** {s['영역']}")
                    st.write(f"**복지카드:** {s['복지']}")
                    for i, g in enumerate(s['목표']):
                        if g['내용']: st.write(f"📍 목표{i+1}: ({g['영역']}) {g['내용']}")

# --- 📝 2. 기록하기 탭 ---
with tab2:
    if not st.session_state.students:
        st.warning("유아 관리 탭에서 아이를 먼저 등록해주세요.")
    else:
        selected_name = st.selectbox("기록할 아이 선택", [s['이름'] for s in st.session_state.students])
        student = next(s for s in st.session_state.students if s['이름'] == selected_name)
        
        st.subheader(f"📊 {selected_name} 어린이 오늘 기록")
        for i, g in enumerate(student['목표']):
            if g['내용']:
                st.info(f"목표 {i+1}: {g['내용']}")
                c1, c2 = st.columns(2)
                with c1:
                    st.button(f"➕ {selected_name} 수행 확인", key=f"btn_{selected_name}_{i}")
                with c2:
                    st.slider("성취도 (%)", 0, 100, 50, key=f"sld_{selected_name}_{i}")
        
        st.text_area("오늘의 누가기록", placeholder="특이사항을 적어주세요.")
        if st.button("🚀 데이터 전송 (임시)"):
            st.balloons()
            st.success("데이터가 전송되었습니다!")

# --- 📊 3. 월간 분석 탭 ---
with tab3:
    st.subheader("📈 성취 추이 (샘플 그래프)")
    st.write("데이터가 쌓이면 여기에 그래프가 나타납니다.")
    # 샘플 그래프
    sample_df = pd.DataFrame({"날짜": ["04-01", "04-05", "04-10", "04-15", "04-19"], "성취도": [20, 45, 40, 60, 85]})
    fig = px.line(sample_df, x="날짜", y="성취도", title="성취도 변화 추이 (예시)")
    st.plotly_chart(fig)
