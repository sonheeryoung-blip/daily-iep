import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. 페이지 설정
st.set_page_config(page_title="매일 기록하는 IEP", page_icon="💙", layout="wide")

# 2. 구글 시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)

# 데이터 초기화
if 'students' not in st.session_state:
    st.session_state.students = []

st.title("💙 매일 기록하는 IEP (연동 완료)")

SPECIAL_AREAS = ["시각장애", "청각장애", "지적장애", "지체장애", "정서·행동장애", "자폐성장애", "의사소통장애", "학습장애", "건강장애", "발달지체"]
DEVELOPMENT_DOMAINS = ["인지", "의사소통", "운동성", "사회정서", "적응행동"]

tab1, tab2 = st.tabs(["📂 유아 관리", "📝 실시간 기록"])

# [유아 관리 탭 - 이전과 동일]
with tab1:
    col_reg, col_list = st.columns([1, 1])
    with col_reg:
        st.subheader("✨ 유아 등록")
        with st.form("reg_form", clear_on_submit=True):
            name = st.text_input("아이 이름")
            class_name = st.text_input("통합학급")
            goals = []
            for i in range(1, 9):
                with st.expander(f"목표 {i}"):
                    d = st.selectbox(f"영역", DEVELOPMENT_DOMAINS, key=f"d{i}")
                    t = st.text_input(f"내용", key=f"t{i}")
                    goals.append({"영역": d, "내용": t})
            if st.form_submit_button("등록"):
                st.session_state.students.append({"이름": name, "학급": class_name, "목표": goals})
                st.rerun()

# [기록하기 탭 - 실제 전송 기능 포함]
with tab2:
    if st.session_state.students:
        selected_name = st.selectbox("유아 선택", [s['이름'] for s in st.session_state.students])
        student = next(s for s in st.session_state.students if s['이름'] == selected_name)
        
        # 기록 폼
        with st.form("record_form"):
            st.subheader(f"📝 {selected_name} 어린이 누가기록")
            record_list = []
            for i, g in enumerate(student['목표']):
                if g['내용']:
                    st.write(f"**[{g['영역']}] {g['내용']}**")
                    c1, c2 = st.columns(2)
                    with c1: count = st.number_input("수행 횟수", 0, 100, 0, key=f"c_{i}")
                    with c2: score = st.slider("성취도(%)", 0, 100, 50, key=f"s_{i}")
                    record_list.append({"영역": g['영역'], "목표": g['내용'], "횟수": count, "성취": score})
            
            note = st.text_area("오늘의 총평/누가기록")
            
            if st.form_submit_button("🚀 구글 시트로 전송"):
                # 전송용 데이터 프레임 만들기
                new_rows = []
                for r in record_list:
                    new_rows.append({
                        "날짜": pd.Timestamp.now().strftime("%Y-%m-%d"),
                        "이름": selected_name,
                        "영역": r['영역'],
                        "세부목표": r['목표'],
                        "수행횟수": r['횟수'],
                        "성취도": r['성취'],
                        "누가기록": note
                    })
                
                # 기존 데이터 읽어와서 합치기
                existing_data = conn.read(worksheet="Record")
                updated_data = pd.concat([existing_data, pd.DataFrame(new_rows)], ignore_index=True)
                
                # 시트 업데이트
                conn.update(worksheet="Record", data=updated_data)
                st.balloons()
                st.success("금고에 데이터가 저장되었습니다!")
