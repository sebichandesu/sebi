import streamlit as st
import pandas as pd
import requests
from datetime import date, timedelta

import storage

st.set_page_config(page_title="나만의 기록장", page_icon="📒", layout="wide")

# ==================== 커스텀 스타일 ====================
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

/* 히어로 헤더 */
.hero {
    background: linear-gradient(135deg, #6C5CE7 0%, #A29BFE 100%);
    padding: 2.2rem 2rem;
    border-radius: 20px;
    margin-bottom: 1.6rem;
    box-shadow: 0 8px 24px rgba(108, 92, 231, 0.18);
}
.hero h1 {
    font-size: 1.9rem;
    font-weight: 900;
    margin: 0 0 0.35rem 0;
    color: #FFFFFF;
}
.hero p {
    font-size: 0.95rem;
    margin: 0;
    color: rgba(255,255,255,0.9);
}

/* 탭 */
button[data-baseweb="tab"] {
    font-size: 1rem;
    font-weight: 700;
    padding: 0.7rem 1.2rem;
    color: #6b6b76;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #6C5CE7;
}
div[data-baseweb="tab-highlight"] {
    background-color: #6C5CE7;
    height: 3px;
}
div[data-baseweb="tab-border"] {
    background-color: #ECECF6;
}

/* 섹션 소제목 */
.section-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #2D2D2D;
    margin: 0.2rem 0 1rem 0;
}

/* 폼(카드) */
div[data-testid="stForm"] {
    background-color: #FAFAFE;
    border: 1px solid #ECECF6;
    border-radius: 18px;
    padding: 1.4rem 1.5rem 0.7rem 1.5rem;
    box-shadow: 0 2px 14px rgba(108, 92, 231, 0.07);
}

/* 버튼 */
.stButton > button, .stFormSubmitButton > button {
    border-radius: 10px;
    font-weight: 700;
    border: none;
    padding: 0.5rem 1.3rem;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    box-shadow: 0 4px 12px rgba(108, 92, 231, 0.25);
}

/* 메트릭 카드 */
div[data-testid="stMetric"] {
    background-color: #FAFAFE;
    border: 1px solid #ECECF6;
    border-radius: 16px;
    padding: 1rem 1.1rem;
    box-shadow: 0 2px 10px rgba(108, 92, 231, 0.06);
}
div[data-testid="stMetricLabel"] {
    font-weight: 600;
    color: #6b6b76;
}

/* 알림 박스 */
div[data-testid="stAlert"] {
    border-radius: 12px;
}

/* 데이터프레임 */
div[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid #ECECF6;
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background-color: #FAFAFE;
    border-right: 1px solid #ECECF6;
}
.sidebar-badge {
    display: inline-block;
    padding: 0.35rem 0.8rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 700;
    margin-bottom: 0.4rem;
}
.badge-on {
    background-color: #E9F9F0;
    color: #1E9E5A;
}
.badge-off {
    background-color: #FFF6E5;
    color: #B77B00;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==================== 사이드바 ====================
st.sidebar.markdown("### 📒 나만의 기록장")
_mode = storage.storage_mode()
if _mode == "oauth":
    st.sidebar.markdown(
        '<span class="sidebar-badge badge-on">🟢 Google Sheets 연결됨 (OAuth)</span>',
        unsafe_allow_html=True,
    )
    st.sidebar.caption("기록이 구글 시트에 영구 저장돼요.")
elif _mode == "apps_script":
    st.sidebar.markdown(
        '<span class="sidebar-badge badge-on">🟢 Apps Script 연결됨</span>',
        unsafe_allow_html=True,
    )
    st.sidebar.caption("기록이 구글 시트에 영구 저장돼요.")
elif _mode == "gsheets":
    st.sidebar.markdown(
        '<span class="sidebar-badge badge-on">🟢 Google Sheets 연결됨</span>',
        unsafe_allow_html=True,
    )
    st.sidebar.caption("기록이 구글 시트에 영구 저장돼요.")
else:
    st.sidebar.markdown(
        '<span class="sidebar-badge badge-off">🟡 로컬 테스트 모드</span>',
        unsafe_allow_html=True,
    )
    st.sidebar.caption("앱 재시작 시 기록이 사라질 수 있어요. SETUP_GUIDE.md 참고해서 연결해보세요.")

# ==================== 헤더 ====================
st.markdown(
    """
    <div class="hero">
        <h1>📒 나만의 기록장</h1>
        <p>오늘의 옷차림, 기분, 소비, 습관을 한 곳에서 가볍게 기록해보세요.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["👕 옷 기록", "😂 짤 뽑기", "📚 책/영화", "💰 가계부", "🔥 습관 트래커"]
)

# ==================== 1. 옷 기록 ====================
with tab1:
    df = storage.load_df("Outfits")
    st.markdown(f'<p class="section-title">오늘 뭐 입었지? · 총 {len(df)}개 기록</p>', unsafe_allow_html=True)

    with st.form("outfit_form", clear_on_submit=True):
        c1, c2 = st.columns([1, 2])
        with c1:
            d = st.date_input("날짜", value=date.today(), key="outfit_date")
        with c2:
            outfit = st.text_input("오늘 옷차림", placeholder="예: 청바지 + 니트 + 스니커즈")
        memo = st.text_input("메모 (선택)", placeholder="예: 좀 더웠음", key="outfit_memo")
        submitted = st.form_submit_button("✏️ 기록하기", use_container_width=True)
        if submitted:
            if outfit.strip():
                storage.append_row(
                    "Outfits", {"날짜": str(d), "옷차림": outfit, "메모": memo}
                )
                st.success("기록했어요!")
                st.rerun()
            else:
                st.warning("옷차림을 입력해주세요.")

    st.write("")
    if not df.empty:
        st.dataframe(
            df.sort_values("날짜", ascending=False), use_container_width=True, hide_index=True
        )
    else:
        st.caption("아직 기록이 없어요. 첫 옷차림을 기록해보세요 👗")

# ==================== 2. 짤 뽑기 ====================
with tab2:
    st.markdown('<p class="section-title">기분 전환이 필요할 때 😊</p>', unsafe_allow_html=True)

    def _fetch_meme():
        try:
            res = requests.get("https://meme-api.com/gimme", timeout=6)
            res.raise_for_status()
            st.session_state["meme"] = res.json()
        except Exception:
            st.session_state["meme"] = None

    if "meme" not in st.session_state:
        _fetch_meme()

    col_a, col_b = st.columns([1, 3])
    with col_a:
        if st.button("🎲 랜덤 짤 뽑기", use_container_width=True):
            _fetch_meme()

    meme = st.session_state.get("meme")
    if meme:
        st.image(meme.get("url"), caption=meme.get("title"), use_container_width=True)
    else:
        st.warning("짤을 불러오지 못했어요. 버튼을 다시 눌러보세요.")

# ==================== 3. 책/영화 기록 ====================
with tab3:
    df = storage.load_df("Media")
    st.markdown(f'<p class="section-title">책 / 영화 기록 · 총 {len(df)}개 기록</p>', unsafe_allow_html=True)

    with st.form("media_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            d = st.date_input("날짜", value=date.today(), key="media_date")
        with c2:
            kind = st.radio("종류", ["책", "영화"], horizontal=True, key="media_kind")
        with c3:
            title = st.text_input("제목", key="media_title")
        rating = st.slider("별점", 1, 5, 3, key="media_rating")
        review = st.text_area("감상평 (선택)", key="media_review")
        submitted = st.form_submit_button("✏️ 기록하기", use_container_width=True)
        if submitted:
            if title.strip():
                storage.append_row(
                    "Media",
                    {
                        "날짜": str(d),
                        "종류": kind,
                        "제목": title,
                        "별점": rating,
                        "감상평": review,
                    },
                )
                st.success("기록했어요!")
                st.rerun()
            else:
                st.warning("제목을 입력해주세요.")

    st.write("")
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("총 기록 수", len(df))
        try:
            col2.metric("평균 별점", f"{round(pd.to_numeric(df['별점']).mean(), 1)} ⭐")
        except Exception:
            pass
        col3.metric("책 / 영화", f"{(df['종류']=='책').sum()} / {(df['종류']=='영화').sum()}")
        st.dataframe(
            df.sort_values("날짜", ascending=False), use_container_width=True, hide_index=True
        )
    else:
        st.caption("아직 기록이 없어요. 최근에 본 책이나 영화를 남겨보세요 🎬")

# ==================== 4. 가계부 ====================
with tab4:
    df = storage.load_df("Expenses")
    st.markdown(f'<p class="section-title">가계부 · 총 {len(df)}건</p>', unsafe_allow_html=True)

    with st.form("expense_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            d = st.date_input("날짜", value=date.today(), key="expense_date")
        with c2:
            category = st.selectbox(
                "카테고리", ["식비", "교통", "쇼핑", "문화생활", "고정비", "기타"], key="expense_cat"
            )
        with c3:
            amount = st.number_input("금액", min_value=0, step=1000, key="expense_amount")
        memo = st.text_input("메모 (선택)", key="expense_memo")
        submitted = st.form_submit_button("✏️ 기록하기", use_container_width=True)
        if submitted:
            if amount > 0:
                storage.append_row(
                    "Expenses",
                    {"날짜": str(d), "카테고리": category, "금액": amount, "메모": memo},
                )
                st.success("기록했어요!")
                st.rerun()
            else:
                st.warning("금액을 입력해주세요.")

    st.write("")
    if not df.empty:
        df["금액"] = pd.to_numeric(df["금액"], errors="coerce")
        col1, col2 = st.columns(2)
        col1.metric("총 지출", f"{int(df['금액'].sum()):,}원")
        col2.metric("이번 기록 건수", len(df))
        chart_df = df.groupby("카테고리")["금액"].sum()
        st.bar_chart(chart_df, color="#6C5CE7")
        st.dataframe(
            df.sort_values("날짜", ascending=False), use_container_width=True, hide_index=True
        )
    else:
        st.caption("아직 기록이 없어요. 오늘 쓴 돈을 남겨보세요 💸")

# ==================== 5. 습관 트래커 ====================
with tab5:
    df = storage.load_df("Habits")
    habit_count = df["습관"].dropna().nunique() if not df.empty else 0
    st.markdown(f'<p class="section-title">습관 트래커 · {habit_count}개 습관 관리 중</p>', unsafe_allow_html=True)

    with st.form("habit_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            d = st.date_input("날짜", value=date.today(), key="habit_date")
        with c2:
            habit = st.text_input("습관 이름", placeholder="예: 물 마시기, 운동, 독서", key="habit_name")
        with c3:
            done = st.checkbox("완료했어요", value=True, key="habit_done")
        submitted = st.form_submit_button("✏️ 기록하기", use_container_width=True)
        if submitted:
            if habit.strip():
                storage.append_row(
                    "Habits", {"날짜": str(d), "습관": habit, "완료": done}
                )
                st.success("기록했어요!")
                st.rerun()
            else:
                st.warning("습관 이름을 입력해주세요.")

    st.write("")
    if not df.empty:
        habits = df["습관"].dropna().unique()
        if len(habits) > 0:
            cols = st.columns(len(habits))
            for i, h in enumerate(habits):
                hdf = df[df["습관"] == h]
                hdf = hdf[hdf["완료"].astype(str).isin(["True", "true", "1"])]
                done_dates = set(pd.to_datetime(hdf["날짜"], errors="coerce").dt.date.dropna())
                streak = 0
                cur = date.today()
                while cur in done_dates:
                    streak += 1
                    cur -= timedelta(days=1)
                with cols[i]:
                    st.metric(h, f"🔥 {streak}일 연속")
        st.dataframe(
            df.sort_values("날짜", ascending=False), use_container_width=True, hide_index=True
        )
    else:
        st.caption("아직 기록이 없어요. 오늘부터 만들고 싶은 습관을 기록해보세요 💪")
