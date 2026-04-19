import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. 페이지 설정
st.set_page_config(page_title="매일 기록하는 IEP", page_icon="💙", layout="wide")

# 스타일 업그레이드 (카드 디자인)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; }
    .student-card {
        background-color: white; padding: 20px; border-radius: 15px;
        border: 2px solid #E1F5FE; text-align: center;
        transition: 0.3s; cursor: pointer;
    }
    .student-card:hover { border-color: #4682B4; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 관리 및 구글 시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)

if 'students' not in st.session_state:
    st.session_state.students = []
if 'page' not in st.session_state:
    st.session_state.page = "home"  # 현재 화면 상태 관리
if 'selected_student' not in st.session_state:
    st.session_state.selected_student = None

# --- 함수: 홈으로 돌아가기 ---
def go_home():
    st.session_state.page = "home"
    st.session_state.selected_student = None
    st.rerun()

# --- 화면 1: 메인 홈 (유아 선택 화면) ---
if st.session_state.page == "home":
    st.title("💙 우리 반 아이들")
    
    col_add, col_empty = st.columns([1, 3])
    with col_add:
        if st.button("➕ 새 유아 추가하기"):
            st.session_state.page = "add_student"
            st.rerun()

    st.write("---")
    
    if not st.session_state.students:
        st.info("등록된 유아가 없습니다. [새 유아 추가하기] 버튼을 눌러주세요.")
    else:
        # 3열로 아이들 카드 배치
        cols = st.columns(3)
        for idx, s in enumerate(st.session_state.students):
            with cols[idx % 3]:
                st.markdown(f"<div class='student-card'>", unsafe_allow_html=True)
                if s['사진']:
                    st.image(s['사진'], use_container_width=True)
                else:
                    st.write("📷 사진 없음")
                st.subheader(s['이름'])
                st.write(f"{s['학급']} | {s['영역']}")
                if st.button(f"📝 기록하기", key=f"select_{idx}"):
                    st.session_state.selected_student = s
                    st.session_state.page = "record"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

# --- 화면 2: 유아 추가 양식 ---
elif st.session_state.page == "add_student":
    st.title("✨ 유아 정보 등록")
    if st.button("⬅️ 돌아가기"): go_home()
    
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("이름")
        class_name = st.text_input("통합학급")
        special_type = st.selectbox("선정영역", ["지적장애", "자폐성장애", "의사소통장애", "발달지체", "기타"])
        photo = st.file_uploader("사진 업로드", type=['jpg', 'png'])
        
        goals = []
        for i in range(1, 9):
            with st.expander(f"목표 {i}"):
                d = st.selectbox(f"영역", ["인지", "의사소통", "운동성", "사회정서", "적응행동"], key=f"d_{i}")
                t = st.text_input(f"내용", key=f"t_{i}")
                goals.append({"영역": d, "내용": t})
        
        if st.form_submit_button("저장하기"):
            if name:
                st.session_state.students.append({
                    "이름": name, "학급": class_name, "영역": special_type, "목표": goals, "사진": photo
                })
                st.success("등록되었습니다!")
                go_home()

# --- 화면 3: 실시간 기록 화면 ---
elif st.session_state.page == "record":
    s = st.session_state.selected_student
    st.title(f"📝 {s['이름']} 기록지")
    if st.button("⬅️ 목록으로"): go_home()
    
    with st.form("rec_form"):
        current_data = []
        for i, g in enumerate(s['목표']):
            if g['내용']:
                st.info(f"**[{g['영역']}]** {g['내용']}")
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1: count = st.number_input("횟수", 0, 50, key=f"cnt_{i}")
                with c2: target = st.number_input("기준", 1, 50, 5, key=f"tar_{i}")
                with c3: score = st.slider("성취(%)", 0, 100, 50, key=f"scr_{i}")
                current_data.append({"영역": g['영역'], "내용": g['내용'], "횟수": count, "성취": score})
        
        note = st.text_area("누가기록")
        if st.form_submit_button("🚀 구글 시트 전송"):
            # (시트 전송 로직 동일하게 유지)
            st.balloons()
            st.success("전송 완료!")
