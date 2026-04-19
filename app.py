import streamlit as st
import pandas as pd
import plotly.express as px # 그래프를 위한 라이브러리
from streamlit_gsheets import GSheetsConnection # 구글 시트 연결 라이브러리

# 1. 페이지 설정
st.set_page_config(page_title="매일 기록하는 IEP", layout="wide")

# 2. 구글 시트 연결 (설정값은 Streamlit Cloud의 Secrets에 저장)
conn = st.connection("gsheets", type=GSheetsConnection)

# 데이터 불러오기 (시트의 'Record' 탭 읽기)
try:
    df = conn.read(worksheet="Record")
except:
    # 시트가 비어있을 경우를 대비한 기본 틀
    df = pd.DataFrame(columns=["날짜", "이름", "발달영역", "세부목표", "수행횟수", "성취도"])

st.title("💙 매일 기록하는 IEP: 분석 및 전송")

tab1, tab2, tab3 = st.tabs(["📂 유아 관리", "📝 기록하기", "📊 월간 분석"])

# --- [tab1, tab2는 이전과 동일하게 유지하되 전송 로직만 추가] ---

with tab2:
    # (중략) ... 기록 로직 수행 후 ...
    if st.button("🚀 데이터 전송 및 시트 업데이트"):
        # 새로운 행 생성
        new_data = pd.DataFrame([{
            "날짜": pd.Timestamp.now().strftime("%Y-%m-%d"),
            "이름": st.session_state.current_student['이름'],
            "발달영역": "사회정서", # 예시
            "수행횟수": st.session_state.count_key, # 예시
            "성취도": 85 # 슬라이더 값 예시
        }])
        
        # 구글 시트에 업데이트 (기존 데이터 + 새 데이터)
        updated_df = pd.concat([df, new_data], ignore_index=True)
        conn.update(worksheet="Record", data=updated_df)
        
        st.balloons()
        st.success("구글 시트로 데이터가 안전하게 전송되었습니다!")

with tab3:
    st.subheader("📈 유아별 성취 추이 분석")
    
    if df.empty:
        st.info("아직 분석할 데이터가 없습니다.")
    else:
        # 1. 필터링 (아이 선택)
        selected_child = st.selectbox("분석할 유아 선택", df['이름'].unique())
        child_df = df[df['이름'] == selected_child]
        
        # 2. 시각화 (Plotly 사용)
        # 날짜별 성취도 변화 그래프
        fig = px.line(child_df, x="날짜", y="성취도", color="발달영역",
                      title=f"[{selected_child}] 어린이 성취도 변화",
                      markers=True, line_shape="spline")
        
        # 하늘색 테마 적용
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#4682B4"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 3. 이번 달 요약 통계
        col1, col2 = st.columns(2)
        with col1:
            avg_score = child_df['성취도'].mean()
            st.metric("평균 성취도", f"{avg_score:.1f}%", delta=f"{avg_score - 50:.1f}%")
        with col2:
            total_count = child_df['수행횟수'].sum()
            st.metric("총 수행 횟수", f"{total_count}회")
