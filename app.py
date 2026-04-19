import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="매일 기록하는 IEP", page_icon="💙", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F8FBFF; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #E1F5FE; border-radius: 5px 5px 0px 0px; padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #B3E5FC !important; font-weight: bold; }
    .goal-box {
        background-color: #F0F8FF; padding: 10px; border-radius: 8px;
        margin-bottom: 5px; border-left: 5px solid #4682B4;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 구글 시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)

# 데이터 초기화
if 'students' not in st.session_state:
    st.session_state.students = []

st.title("💙 매일 기록하는 IEP")

# 범주 데이터
SPECIAL_AREAS = ["시각장애", "청각장애", "지적장애", "지체장애", "정서·행동장애", "자폐성장애", "의사소통장애", "학습장애", "건강장애", "발달지체"]
DEVELOPMENT_DOMAINS = ["인지", "의사소통", "운동성", "사회정서", "적응행동"]

tab1, tab2, tab3 = st.tabs(["📂 유아 관리", "📝 실시간 기록", "📊 월간 분석"])

# --- 📂 1. 유아 관리 (등록 및 목록) ---
with tab1:
    col_reg, col_list = st.columns([1, 1])
    
    with col_reg:
        st.subheader("✨ 새로운 유아 등록")
        with st.form("student_form", clear_on_submit=True):
            name = st.text_input("아이 이름")
            birth = st.date_input("생년월일", value=pd.to_datetime("2021-01-01"))
            class_name = st.text_input("통합학급")
            special_type = st.selectbox("특수교육대상 선정영역", SPECIAL_AREAS)
            welfare_card = st.text_input("복지카드 정보 (자유 작성)")
            photo = st.file_uploader("유아 사진 업로드", type=['jpg', 'png', 'jpeg'])
            
            st.write("---")
            st.write("🎯 **IEP 세부 목표 설정 (최대 8개)**")
            goals = []
            for i in range(1, 9):
                with st.expander(f"📍 목표 {i} 설정"):
                    c1, c2 = st.columns([1, 2])
                    with c1: d = st.selectbox(f"영역", DEVELOPMENT_DOMAINS, key=f"dom_{i}")
                    with c2: t = st.text_input(f"세부내용", key=f"txt_{i}")
                    goals.append({"영역": d, "내용": t})
            
            if st.form_submit_button("등록 완료"):
                if name:
                    st.session_state.students.append({
                        "이름": name, "생일": birth.strftime("%Y-%m-%d"), 
                        "학급": class_name, "영역": special_type, 
                        "복지": welfare_card, "목표": goals, "사진": photo
                    })
                    st.success(f"{name} 등록 완료!")
                    st.rerun()

    with col_list:
        st.subheader("👥 우리 반 목록")
        for s in st.session_state.students:
            with st.expander(f"👤 {s['이름']} ({s['학급']})"):
                if s['사진']: st.image(s['사진'], width=150)
                st.write(f"🎂 생일: {s['생일']}")
                st.write(f"📂 영역: {s['영역']} | 복지: {s['복지']}")

# --- 📝 2. 실시간 기록 (구글 시트 전송 포함) ---
with tab2:
    if not st.session_state.students:
        st.info("유아를 먼저 등록해주세요.")
    else:
        selected_name = st.selectbox("기록할 아이 선택", [s['이름'] for s in st.session_state.students])
        student = next(s for s in st.session_state.students if s['이름'] == selected_name)
        
        with st.form("record_form"):
            st.subheader(f"📊 {selected_name} 어린이 실시간 기록")
            current_records = []
            for i, g in enumerate(student['목표']):
                if g['내용']:
                    st.markdown(f"<div class='goal-box'><b>[{g['영역']}]</b> {g['내용']}</div>", unsafe_allow_html=True)
                    c1, c2, c3 = st.columns([1, 1, 2])
                    with c1: count = st.number_input("수행 횟수", 0, 50, 0, key=f"c_{selected_name}_{i}")
                    with c2: target = st.number_input("기준 횟수", 1, 50, 5, key=f"t_{selected_name}_{i}")
                    with c3: score = st.slider("성취도(%)", 0, 100, 50, key=f"s_{selected_name}_{i}")
                    current_records.append({"영역": g['영역'], "내용": g['내용'], "횟수": count, "성취": score})
            
            note = st.text_area("누가기록/특이사항")
            
            if st.form_submit_button("🚀 구글 시트로 데이터 전송"):
                # 시트 전송 로직
                new_rows = []
                for r in current_records:
                    new_rows.append({
                        "날짜": pd.Timestamp.now().strftime("%Y-%m-%d"),
                        "이름": selected_name, "영역": r['영역'], "세부목표": r['내용'],
                        "수행횟수": r['횟수'], "성취도": r['성취'], "누가기록": note
                    })
                try:
                    existing_df = conn.read(worksheet="Record")
                    updated_df = pd.concat([existing_df, pd.DataFrame(new_rows)], ignore_index=True)
                    conn.update(worksheet="Record", data=updated_df)
                    st.balloons()
                    st.success("구글 시트에 성공적으로 저장되었습니다!")
                except:
                    st.error("시트 연동에 문제가 발생했습니다. Secrets 설정을 확인해주세요.")

# --- 📊 3. 월간 분석 ---
with tab3:
    st.info("시트에 데이터가 쌓이면 분석 그래프가 활성화됩니다.")
