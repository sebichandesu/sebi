import calendar as cal_module
import html
import json
from urllib.parse import quote as _urlquote

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import date, timedelta, datetime

import storage

st.set_page_config(page_title="말랑 다이어리", page_icon="🍡", layout="wide")

# ==================== 커스텀 스타일 ====================
CUSTOM_CSS = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');

:root {
    --accent: #2DD4BF;
    --accent-2: #38BDF8;
    --accent-soft: #E7FBF8;
    --surface: #FFFFFF;
    --border: #DCEEEC;
    --input-border: #C7D6D9;
    --text-main: #1C2B2A;
    --text-sub: #6B8C89;
}

html, body, [class*="css"],
h1, h2, h3, h4, h5, h6, p, span, label, div, button, input, textarea, select {
    font-family: 'Pretendard', 'Malgun Gothic', 'Apple SD Gothic Neo',
        -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: var(--text-main);
}

/* 전체 폭을 적당히 제한하고 여백을 넉넉하게 */
div[data-testid="stMainBlockContainer"], .main .block-container {
    max-width: 900px !important;
    padding-top: 2.4rem !important;
    padding-bottom: 3.5rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
}
div[data-testid="stVerticalBlock"] {
    gap: 1.1rem;
}

/* 히어로 헤더 */
.hero {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
    padding: 2rem 2.2rem;
    border-radius: 20px;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(20, 184, 166, 0.22);
}
.hero-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    flex-wrap: wrap;
}
.hero h1 {
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    margin: 0 0 0.4rem 0;
    color: #FFFFFF;
}
.hero p {
    font-size: 0.95rem;
    margin: 0;
    color: rgba(255,255,255,0.9);
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,0.2);
    backdrop-filter: blur(4px);
    color: #FFFFFF;
    padding: 0.45rem 0.9rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    white-space: nowrap;
}

/* 탭 - 세그먼트(알약) 스타일 */
div[data-baseweb="tab-list"] {
    gap: 4px;
    background-color: var(--accent-soft);
    padding: 6px;
    border-radius: 14px;
    margin-bottom: 1.8rem;
}
button[data-baseweb="tab"] {
    height: auto;
    font-size: 0.92rem;
    font-weight: 600;
    padding: 0.6rem 1.1rem;
    color: var(--text-sub);
    border-radius: 10px;
    border: none;
    background-color: transparent;
    transition: background-color 0.15s ease, color 0.15s ease;
}
button[data-baseweb="tab"]:hover {
    color: var(--accent);
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent);
    background-color: #FFFFFF;
    box-shadow: 0 3px 10px rgba(20, 184, 166, 0.16);
}
div[data-baseweb="tab-highlight"] {
    display: none;
}
div[data-baseweb="tab-border"] {
    display: none;
}

/* 섹션 소제목 */
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    color: var(--text-main);
    margin: 0.3rem 0 1.1rem 0;
}
.sub-label {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-sub);
    margin: 0.7rem 0 0.4rem 0;
}

/* 폼(카드) */
div[data-testid="stForm"] {
    background-color: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.7rem 1.8rem 1rem 1.8rem;
    box-shadow: 0 2px 16px rgba(20, 184, 166, 0.07);
    margin-bottom: 2rem;
}
div[data-testid="stForm"] label p {
    font-weight: 600;
    font-size: 0.8rem;
    color: var(--text-sub);
}
.st-key-outfit_form_card {
    background-color: var(--surface);
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 1.7rem 1.8rem 1rem 1.8rem !important;
    box-shadow: 0 2px 16px rgba(20, 184, 166, 0.07);
    margin-bottom: 2rem;
}
.st-key-outfit_form_card label p {
    font-weight: 600;
    font-size: 0.8rem;
    color: var(--text-sub);
}

/* 버튼 - 공통 */
.stButton > button, .stFormSubmitButton > button {
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.92rem;
    padding: 0.65rem 1.4rem;
    cursor: pointer;
    transition: transform 0.16s cubic-bezier(0.34, 1.56, 0.64, 1),
        box-shadow 0.16s ease, filter 0.16s ease, background-color 0.16s ease,
        border-color 0.16s ease;
}

/* 기본(보조) 버튼 - 흰 배경 + 민트 테두리 */
.stButton > button, .stFormSubmitButton > button {
    background-color: #FFFFFF;
    color: var(--accent);
    border: 1.5px solid var(--accent);
    box-shadow: 0 2px 6px rgba(45, 212, 191, 0.14);
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background-color: var(--accent-soft);
    box-shadow: 0 6px 14px rgba(45, 212, 191, 0.28), 0 0 0 4px rgba(45, 212, 191, 0.12);
    transform: translateY(-2px) scale(1.02);
}
.stButton > button:active, .stFormSubmitButton > button:active {
    transform: translateY(0) scale(0.95);
    box-shadow: 0 1px 3px rgba(45, 212, 191, 0.2);
    filter: brightness(0.97);
}

/* 주요(primary) 버튼 - 꽉 찬 민트, 핵심 액션(기록하기)에만 사용 */
button[data-testid*="primary"] {
    background-color: var(--accent) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 3px 8px rgba(45, 212, 191, 0.35) !important;
}
button[data-testid*="primary"]:hover {
    box-shadow: 0 8px 18px rgba(45, 212, 191, 0.4), 0 0 0 4px rgba(45, 212, 191, 0.16) !important;
    transform: translateY(-2px) scale(1.02);
    filter: brightness(1.05);
}
button[data-testid*="primary"]:active {
    transform: translateY(0) scale(0.95);
    filter: brightness(0.95);
    box-shadow: 0 2px 4px rgba(45, 212, 191, 0.3) !important;
}

/* 위험(삭제) 버튼 */
.st-key-Outfits_delete_btn button, .st-key-Media_delete_btn button,
.st-key-Expenses_delete_btn button, .st-key-Habits_delete_btn button,
.st-key-outfit_cal_delete_btn button {
    background-color: #FFFFFF !important;
    color: #E11D48 !important;
    border: 1.5px solid #FDA4AF !important;
    box-shadow: 0 2px 6px rgba(225, 29, 72, 0.12) !important;
}
.st-key-Outfits_delete_btn button:hover, .st-key-Media_delete_btn button:hover,
.st-key-Expenses_delete_btn button:hover, .st-key-Habits_delete_btn button:hover,
.st-key-outfit_cal_delete_btn button:hover {
    background-color: #FFF1F2 !important;
    border-color: #E11D48 !important;
    box-shadow: 0 6px 14px rgba(225, 29, 72, 0.22) !important;
    transform: translateY(-2px) scale(1.02);
}

/* 달력 이동(◀▶) - 미니멀 고스트 버튼 */
.st-key-outfit_cal_prev button, .st-key-outfit_cal_next button {
    background-color: transparent !important;
    color: var(--text-sub) !important;
    border: 1.5px solid var(--border) !important;
    box-shadow: none !important;
    border-radius: 10px;
    padding: 0.45rem 0.9rem;
}
.st-key-outfit_cal_prev button:hover, .st-key-outfit_cal_next button:hover {
    color: var(--accent) !important;
    border-color: var(--accent) !important;
    background-color: var(--accent-soft) !important;
    box-shadow: none !important;
    transform: translateY(-1px);
}

/* 달력 날짜 셀(클릭 가능) */
div[class*="st-key-outfit_cal_day_"] button {
    background-color: var(--surface) !important;
    color: var(--text-main) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    box-shadow: none !important;
    min-height: 58px;
    padding: 0.45rem 0.2rem 0.7rem 0.2rem !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    display: flex !important;
    align-items: flex-start !important;
    justify-content: center !important;
    transform: none !important;
}
div[class*="st-key-outfit_cal_day_"] button:hover {
    background-color: var(--accent-soft) !important;
    border-color: var(--accent) !important;
    box-shadow: none !important;
    transform: none !important;
}
div[class*="st-key-outfit_cal_day_"] button:active {
    background-color: var(--accent-soft) !important;
    transform: scale(0.95) !important;
}
div[class*="__dim"] button {
    opacity: 0.32;
}
div[class*="__today"] button {
    border: 2px solid var(--accent) !important;
    font-weight: 700 !important;
}
/* 날짜 버튼 + 아래 색상 점(dots)이 한 칸처럼 붙어 보이도록 그 칸의 세로 간격만 좁힘 */
div[data-testid="stVerticalBlock"]:has(> div[class*="st-key-outfit_cal_day_"]) {
    gap: 0.25rem !important;
}
/* 달력 그리드 전체(주 단위 행들) 간격도 좁혀서 촘촘한 달력처럼 보이게 */
div[class*="st-key-outfit_cal_grid"] div[data-testid="stVerticalBlock"] {
    gap: 0.4rem !important;
}
.cal-dots {
    min-height: 12px;
}

/* 메트릭 카드 */
div[data-testid="stMetric"] {
    background-color: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.1rem 1.2rem;
    box-shadow: 0 2px 10px rgba(20, 184, 166, 0.06);
}
div[data-testid="stMetricLabel"] {
    font-weight: 600;
    color: var(--text-sub);
}

/* 알림 박스 */
div[data-testid="stAlert"] {
    border-radius: 12px;
}
div[data-testid="stAlertContentSuccess"] {
    background-color: #ECFDF5 !important;
    color: #047857 !important;
}
div[data-testid="stAlertContentSuccess"] svg {
    fill: #10B981 !important;
}

/* 기록하기 폼을 접었다 펼 수 있는 expander - 카드 톤에 맞춤
   (overflow:hidden을 주면 펼쳤을 때 안쪽 내용이 잘려 보이는 문제가 있어서 뺌 - 둥근
   모서리는 border-radius만으로도 배경/테두리에 충분히 적용돼요) */
div[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    background-color: var(--surface);
    margin-bottom: 0.5rem;
    box-shadow: 0 2px 12px rgba(20, 184, 166, 0.05);
}
div[data-testid="stExpanderDetails"] {
    overflow: visible !important;
}
div[data-testid="stExpander"] summary, div[data-testid="stExpander"] > div:first-child {
    font-weight: 700 !important;
    border-radius: 16px;
}
/* 접힌 상태에서 테두리가 2겹으로 보이는 문제: 바깥 div(stExpander)에 이미 테두리를
   줬는데, 안쪽의 details/첫 자식 div에도 스트림릿 기본 테두리·그림자가 남아있어서
   겹쳐 보임 - 안쪽 요소들은 전부 테두리 없이 투명하게 만들고, 바깥 테두리 하나만
   보이도록 정리 */
div[data-testid="stExpander"] > details,
div[data-testid="stExpander"] > div,
div[data-testid="stExpander"] details > div,
div[data-testid="stExpander"] summary {
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    background: transparent !important;
}

/* 결과/기록 영역 카드 - 폼과 시각적으로 구분 */
.st-key-outfit_results, .st-key-media_results,
.st-key-expense_results, .st-key-habit_results {
    background-color: var(--surface);
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 1.4rem 1.5rem !important;
    box-shadow: 0 2px 12px rgba(20, 184, 166, 0.05);
}

/* 클릭 가능한 요소는 포인터 커서 */
div[data-baseweb="select"], div[data-baseweb="select"] * ,
button[data-baseweb="tab"],
.stCheckbox, .stCheckbox *,
div[data-baseweb="radio"] label,
label[data-baseweb="radio"] {
    cursor: pointer !important;
}

/* 입력창(선택박스/텍스트/날짜/숫자) - 글씨와 구분되도록 테두리 표시 */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"],
div[data-baseweb="base-input"] {
    border: 1.5px solid var(--input-border) !important;
    border-radius: 10px !important;
    background-color: #FFFFFF !important;
    box-shadow: none !important;
}
div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="textarea"]:focus-within,
div[data-baseweb="base-input"]:focus-within {
    border-color: var(--accent) !important;
}
.stDateInput input, .stNumberInput input {
    border-radius: 10px !important;
}

/* 글자 크기 위계: 라벨(0.8rem, 회색)보다 선택된 값/입력한 글씨가 오히려 커 보이던 문제
   (셀렉트박스는 브라우저 기본 크기를 그대로 쓰고 있었음) - 값 글씨 크기를 명시적으로
   지정해서 라벨과 자연스럽게 어울리도록 맞춤. 팝업으로 뜨는 드롭다운 옵션 목록도 동일 크기로. */
div[data-baseweb="select"], div[data-baseweb="select"] *,
div[data-baseweb="input"] input, div[data-baseweb="input"] *,
div[data-baseweb="popover"] li, div[data-baseweb="popover"] *,
ul[role="listbox"], ul[role="listbox"] * {
    font-size: 0.85rem !important;
}
div[data-baseweb="select"] input {
    font-size: 0.85rem !important;
}

/* 데이터프레임 */
div[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid var(--border);
    margin-top: 0.8rem;
}

/* 옷 태그 칩 */
.outfit-tag {
    display: inline-flex;
    align-items: center;
    padding: 5px 12px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    margin: 3px 6px 3px 0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}

/* 기분 잔디밭 히트맵 */
.mood-grid-wrap {
    overflow-x: auto;
    padding-bottom: 4px;
    margin-top: 0.6rem;
}
.mood-grid {
    display: grid;
    grid-auto-flow: column;
    grid-template-rows: repeat(7, 1fr);
    gap: 3px;
    width: fit-content;
}
.mood-cell {
    width: 12px;
    height: 12px;
    border-radius: 3px;
    border: 1px solid var(--border);
}
.mood-cell-hasdata {
    cursor: pointer;
}
.mood-cell-hasdata:hover {
    transform: scale(1.25);
    box-shadow: 0 0 0 1.5px var(--accent);
}
.mood-cell-future {
    background: transparent;
    border: none;
}
.mood-legend {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 0.72rem;
    color: var(--text-sub);
    margin: 0.5rem 0 1rem 0;
}
.mood-legend-dot {
    width: 11px;
    height: 11px;
    border-radius: 3px;
    display: inline-block;
    margin: 0 1px;
}

/* 달력 뷰 */
.cal-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 6px;
    margin: 0.8rem 0 1rem 0;
}
.cal-weekday {
    text-align: center;
    font-size: 0.76rem;
    font-weight: 600;
    color: var(--text-sub);
    padding-bottom: 4px;
}
.cal-cell {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    min-height: 60px;
    padding: 6px 4px 8px 4px;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.cal-cell-dim {
    opacity: 0.32;
}
.cal-cell-today {
    border: 2px solid var(--accent);
}
.cal-daynum {
    font-size: 0.76rem;
    font-weight: 600;
    color: var(--text-main);
}
/* 기분 기록 달력 - 기존 잔디밭 히트맵을 월별로 넘겨보는 방식으로 바꾸면서
   위의 달력 뷰 클래스들을 그대로 재사용. 데이터 있는 칸만 호버 효과를
   달력 칸 크기에 맞게 살짝 조정 */
.cal-cell.mood-cell-hasdata:hover {
    transform: translateY(-2px) scale(1.03);
    box-shadow: 0 4px 10px rgba(0,0,0,0.12), 0 0 0 1.5px var(--accent);
}
.cal-dots {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 3px;
    margin-top: 5px;
}
.cal-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 0 1px rgba(0,0,0,0.08);
}
.cal-month-label {
    text-align: center;
    font-weight: 700;
    font-size: 1rem;
    margin: 0.3rem 0;
    color: var(--text-main);
}

/* 사랑 고백 카드 */
div[class*="st-key-love_note_"] {
    background-color: #FFF7FA !important;
    border: 1px solid #FBCFE8 !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 8px rgba(225, 29, 109, 0.06);
}
.love-note-date {
    font-size: 0.78rem;
    font-weight: 700;
    color: #E11D6D;
}
.love-note-text {
    margin: 0.35rem 0 0 0;
    font-size: 0.92rem;
    line-height: 1.55;
    color: var(--text-main);
    white-space: pre-wrap;
}
div[class*="st-key-love_delete_"] button {
    background-color: transparent !important;
    color: #E11D6D !important;
    border: 1.5px solid #FBCFE8 !important;
    box-shadow: none !important;
    padding: 0.4rem 0.6rem !important;
}
div[class*="st-key-love_delete_"] button:hover {
    background-color: #FFF1F5 !important;
    border-color: #E11D6D !important;
}

/* 모바일 대응 */
@media (max-width: 640px) {
    div[data-testid="stMainBlockContainer"], .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1.4rem !important;
    }
    .hero {
        padding: 1.5rem 1.3rem;
        border-radius: 16px;
        margin-bottom: 1.4rem;
    }
    .hero h1 {
        font-size: 1.35rem;
    }
    .hero p {
        font-size: 0.82rem;
    }
    div[data-baseweb="tab-list"] {
        overflow-x: auto;
        flex-wrap: nowrap;
    }
    button[data-baseweb="tab"] {
        padding: 0.5rem 0.75rem;
        font-size: 0.82rem;
        white-space: nowrap;
    }
    div[data-testid="stForm"], .st-key-outfit_form_card {
        padding: 1.2rem 1.1rem 0.6rem 1.1rem !important;
    }

    /* 옷 기록 달력 - 좁은 화면에서도 요일 헤더/월 이동/날짜 7칸이 줄바꿈되지 않고
       한 줄 그리드로 유지되도록 강제 (기본으로는 칸이 좁아지면 세로로 쌓여서
       달력이 긴 목록처럼 깨져 보임) */
    div[class*="st-key-outfit_cal_nav"] div[data-testid="stHorizontalBlock"],
    div[class*="st-key-outfit_cal_grid"] div[data-testid="stHorizontalBlock"],
    div[class*="st-key-mood_cal_nav"] div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 3px !important;
    }
    div[class*="st-key-outfit_cal_nav"] div[data-testid="stColumn"],
    div[class*="st-key-outfit_cal_grid"] div[data-testid="stColumn"],
    div[class*="st-key-mood_cal_nav"] div[data-testid="stColumn"] {
        min-width: 0 !important;
        width: auto !important;
        flex: 1 1 0 !important;
        padding: 0 1px !important;
    }
    div[class*="st-key-outfit_cal_day_"] button {
        min-height: 38px;
        padding: 0.2rem 0 0.5rem 0 !important;
        font-size: 0.68rem !important;
    }
    .cal-weekday {
        font-size: 0.64rem;
    }
    .cal-month-label {
        font-size: 0.88rem;
    }

    /* 떠있는 위젯(BGM/기분 팝업)이 화면 폭을 넘지 않도록 */
    #mallang-bgm-panel, #mallang-mood-popup {
        max-width: calc(100vw - 40px) !important;
    }

    /* 기분 잔디밭 - 좁은 화면에서는 주 단위로 옆으로 길게 늘어나는 기존 방식 대신
       최근 30일만 6칸씩 줄바꿈되는 달력 느낌의 정사각형 블록으로 보여줌.
       가로 스크롤이 아예 필요 없고, 칸도 훨씬 크게 보여요. */
    .mood-grid-wrap {
        overflow-x: hidden !important;
    }
    .mood-grid {
        display: grid !important;
        grid-auto-flow: row !important;
        grid-template-columns: repeat(6, 1fr) !important;
        grid-template-rows: none !important;
        gap: 6px !important;
        width: 100% !important;
    }
    .mood-cell {
        width: auto !important;
        height: auto !important;
        aspect-ratio: 1 / 1 !important;
        border-radius: 5px !important;
    }
    /* weeks=52 기준 총 364칸 중 마지막 30칸(최근 30일)만 남기고 숨김 */
    .mood-cell:nth-child(-n+334) {
        display: none !important;
    }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==================== 커서 별 이펙트 (캔버스 반짝이 트레일) ====================
STAR_TRAIL_JS = """
<script>
(function() {
    const doc = window.parent.document;
    if (doc.__starTrailInit) return;
    doc.__starTrailInit = true;

    const canvas = doc.createElement('canvas');
    canvas.id = 'mallang-star-canvas';
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '999999';
    doc.body.appendChild(canvas);
    const ctx = canvas.getContext('2d');
    const parentWin = window.parent;

    function resize() {
        canvas.width = parentWin.innerWidth;
        canvas.height = parentWin.innerHeight;
    }
    resize();
    parentWin.addEventListener('resize', resize);

    const sparkleColors = ['#ffffff', '#38BDF8', '#2DD4BF'];
    let particles = [];
    let lastSpawn = 0;

    function drawStar(c, cx, cy, spikes, outerR, innerR) {
        let rot = (Math.PI / 2) * 3;
        const step = Math.PI / spikes;
        c.beginPath();
        c.moveTo(cx, cy - outerR);
        for (let i = 0; i < spikes; i++) {
            let x = cx + Math.cos(rot) * outerR;
            let y = cy + Math.sin(rot) * outerR;
            c.lineTo(x, y);
            rot += step;
            x = cx + Math.cos(rot) * innerR;
            y = cy + Math.sin(rot) * innerR;
            c.lineTo(x, y);
            rot += step;
        }
        c.lineTo(cx, cy - outerR);
        c.closePath();
    }

    doc.addEventListener('mousemove', function(e) {
        const now = performance.now();
        if (now - lastSpawn < 30) return;
        lastSpawn = now;
        particles.push({
            x: e.clientX,
            y: e.clientY,
            size: 3 + Math.random() * 3,
            alpha: 1,
            color: sparkleColors[Math.floor(Math.random() * sparkleColors.length)]
        });
    });

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(function(p) { p.alpha -= 0.045; });
        particles = particles.filter(function(p) { return p.alpha > 0; });
        particles.forEach(function(p) {
            ctx.save();
            ctx.globalAlpha = Math.max(p.alpha, 0);
            ctx.fillStyle = p.color;
            ctx.shadowColor = p.color;
            ctx.shadowBlur = 6;
            drawStar(ctx, p.x, p.y, 5, p.size * 1.8, p.size * 0.8);
            ctx.fill();
            ctx.restore();
        });
        parentWin.requestAnimationFrame(animate);
    }
    animate();
})();
</script>
"""
components.html(STAR_TRAIL_JS, height=0, width=0)


# ==================== 배경음악(BGM) 플레이어 ====================
# 직접 만든 곡을 BGM으로 사용. Streamlit Cloud의 자체 static 서빙(app/static/...)이
# 배포 환경에서 계속 무한로딩(응답 없음)이라 그쪽은 포기하고, 대신 깃헙 repo가
# public이라는 점을 이용해 jsDelivr CDN(공개 repo 파일을 그대로 서빙해주는
# 무료 CDN)에서 바로 mp3를 가져오는 방식으로 바꿈. repo에 static/ 폴더의
# mp3들이 실제로 커밋/푸시되어 있어야 함.
GITHUB_USER = "sebichandesu"
GITHUB_REPO = "sebi"
GITHUB_BRANCH = "main"

BGM_PLAYLIST = [
    {"name": "🫧 거품", "file": "거품.mp3"},
    {"name": "💧 유선형", "file": "유선형.mp3"},
    {"name": "🎐 우음", "file": "우음.mp3"},
]
for _t in BGM_PLAYLIST:
    _t["url"] = (
        f"https://cdn.jsdelivr.net/gh/{GITHUB_USER}/{GITHUB_REPO}@{GITHUB_BRANCH}/"
        f"static/{_urlquote(_t['file'])}"
    )

BGM_PLAYER_JS = f"""
<script>
(function() {{
    const doc = window.parent.document;
    if (doc.__bgmPlayerInit) return;
    doc.__bgmPlayerInit = true;

    const playlist = {json.dumps(BGM_PLAYLIST, ensure_ascii=False)};
    let idx = 0;

    const style = doc.createElement('style');
    style.textContent = `
        #mallang-bgm-wrap {{
            position: fixed; left: 20px; bottom: 20px; z-index: 999998;
            font-family: 'Pretendard','Malgun Gothic',-apple-system,sans-serif;
        }}
        .mallang-bgm-pill {{
            display: flex; align-items: center; gap: 5px; padding: 6px 10px;
            background: #E7FBF8; border: 1px solid #BEEEE7; border-radius: 26px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.14);
        }}
        .mallang-bgm-charm {{ font-size: 14px; opacity: 0.85; transform: rotate(-8deg); animation: mallang-bgm-charm-sway 2.6s ease-in-out infinite; }}
        @keyframes mallang-bgm-charm-sway {{
            0%, 100% {{ transform: translateY(0) rotate(-8deg); }}
            50% {{ transform: translateY(-2px) rotate(6deg); }}
        }}
        #mallang-bgm-toggle {{
            width: 36px; height: 36px; border-radius: 50%; border: 2px solid #fff; cursor: pointer;
            background: linear-gradient(135deg, #2DD4BF 0%, #38BDF8 100%);
            color: #fff; font-size: 15px; box-shadow: 0 2px 8px rgba(45,212,191,0.4);
            display: flex; align-items: center; justify-content: center; position: relative;
            transition: transform 0.15s ease;
        }}
        #mallang-bgm-toggle:hover {{ transform: translateY(-3px) rotate(-8deg) scale(1.12); }}
        #mallang-bgm-toggle:active {{ transform: scale(0.9); }}
        #mallang-bgm-toggle.playing {{ animation: mallang-bgm-pulse 1.2s ease-in-out infinite; }}
        @keyframes mallang-bgm-pulse {{
            0%, 100% {{ box-shadow: 0 2px 8px rgba(45,212,191,0.4), 0 0 0 0 rgba(45,212,191,0.35); }}
            50% {{ box-shadow: 0 2px 8px rgba(45,212,191,0.4), 0 0 0 7px rgba(45,212,191,0); }}
        }}
        #mallang-bgm-toggle::after {{
            content: '음악'; position: absolute; bottom: 130%; left: 50%; transform: translateX(-50%);
            font-size: 10px; font-weight: 700; color: #0F9C87; background: #fff; padding: 3px 8px; border-radius: 10px;
            white-space: nowrap; opacity: 0; pointer-events: none; transition: opacity 0.15s ease, transform 0.15s ease;
            box-shadow: 0 2px 6px rgba(0,0,0,0.12);
        }}
        #mallang-bgm-toggle:hover::after {{ opacity: 1; transform: translateX(-50%) translateY(-2px); }}
        #mallang-bgm-panel {{
            position: absolute; bottom: 58px; left: 0; width: 230px;
            background: #fff; border: 1px solid #DCEEEC; border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.16); padding: 14px;
            display: none;
        }}
        #mallang-bgm-panel.open {{ display: block; }}
        #mallang-bgm-title {{ font-size: 0.78rem; font-weight: 700; color: #6B8C89; margin-bottom: 2px; }}
        #mallang-bgm-track {{ font-size: 0.85rem; font-weight: 700; color: #1C2B2A; margin-bottom: 10px; }}
        .mallang-bgm-controls {{ display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 10px; }}
        .mallang-bgm-controls button {{
            width: 34px; height: 34px; border-radius: 50%; border: 1.5px solid #DCEEEC; background: #fff;
            cursor: pointer; font-size: 13px; color: #1C2B2A; display: flex; align-items: center; justify-content: center;
            transition: transform 0.15s cubic-bezier(0.34, 1.56, 0.64, 1);
        }}
        .mallang-bgm-controls button:hover {{ background: #E7FBF8; border-color: #2DD4BF; transform: scale(1.1); }}
        #mallang-bgm-play {{
            width: 42px; height: 42px; background: #2DD4BF; color: #fff; border-color: #2DD4BF; font-size: 15px;
        }}
        #mallang-bgm-play:hover {{ background: #26bfab; }}
        #mallang-bgm-vol-row {{ display: flex; align-items: center; gap: 6px; font-size: 12px; color: #6B8C89; margin-bottom: 8px; }}
        #mallang-bgm-vol {{ width: 100%; accent-color: #2DD4BF; cursor: pointer; }}
        #mallang-bgm-credit {{ font-size: 10px; color: #9BB5B2; text-align: center; }}
    `;
    doc.head.appendChild(style);

    const wrap = doc.createElement('div');
    wrap.id = 'mallang-bgm-wrap';
    wrap.innerHTML = `
        <div id="mallang-bgm-panel">
            <div id="mallang-bgm-title">🎵 배경음악</div>
            <div id="mallang-bgm-track"></div>
            <div class="mallang-bgm-controls">
                <button id="mallang-bgm-prev" title="이전 곡">⏮</button>
                <button id="mallang-bgm-play" title="재생/일시정지">▶️</button>
                <button id="mallang-bgm-next" title="다음 곡">⏭</button>
            </div>
            <div id="mallang-bgm-vol-row">
                🔈 <input type="range" id="mallang-bgm-vol" min="0" max="100" value="45" />
            </div>
            <div id="mallang-bgm-credit">🎶 내가 만든 노래예요</div>
        </div>
        <div class="mallang-bgm-pill">
            <span class="mallang-bgm-charm">🍡</span>
            <button id="mallang-bgm-toggle" title="음악">🎵</button>
        </div>
    `;
    doc.body.appendChild(wrap);

    const audio = doc.createElement('audio');
    audio.id = 'mallang-bgm-audio';
    audio.preload = 'none';
    doc.body.appendChild(audio);
    audio.volume = 0.45;

    const toggleBtn = wrap.querySelector('#mallang-bgm-toggle');
    const panel = wrap.querySelector('#mallang-bgm-panel');
    const trackLabel = wrap.querySelector('#mallang-bgm-track');
    const playBtn = wrap.querySelector('#mallang-bgm-play');
    const prevBtn = wrap.querySelector('#mallang-bgm-prev');
    const nextBtn = wrap.querySelector('#mallang-bgm-next');
    const volInput = wrap.querySelector('#mallang-bgm-vol');

    function loadTrack(i, autoplay) {{
        idx = (i + playlist.length) % playlist.length;
        audio.src = playlist[idx].url;
        trackLabel.textContent = (idx + 1) + '. ' + playlist[idx].name;
        if (autoplay) {{ audio.play().catch(function() {{}}); }}
    }}

    function updatePlayBtn() {{
        playBtn.textContent = audio.paused ? '▶️' : '⏸️';
        toggleBtn.classList.toggle('playing', !audio.paused);
    }}

    toggleBtn.addEventListener('click', function() {{
        panel.classList.toggle('open');
    }});
    doc.addEventListener('click', function(e) {{
        if (!wrap.contains(e.target)) panel.classList.remove('open');
    }});
    playBtn.addEventListener('click', function() {{
        if (!audio.src) loadTrack(0, false);
        if (audio.paused) {{ audio.play().catch(function() {{}}); }} else {{ audio.pause(); }}
    }});
    prevBtn.addEventListener('click', function() {{ loadTrack(idx - 1, true); }});
    nextBtn.addEventListener('click', function() {{ loadTrack(idx + 1, true); }});
    audio.addEventListener('ended', function() {{ loadTrack(idx + 1, true); }});
    audio.addEventListener('play', updatePlayBtn);
    audio.addEventListener('pause', updatePlayBtn);
    volInput.addEventListener('input', function() {{ audio.volume = volInput.value / 100; }});

    loadTrack(0, false);
    updatePlayBtn();
}})();
</script>
"""
components.html(BGM_PLAYER_JS, height=0, width=0)


# ==================== 기분 잔디밭 클릭 상세보기 ====================
# 잔디밭 칸(.mood-cell-hasdata)을 클릭하면 그날 몇 시에 어떤 기분을 남겼는지
# 작은 팝업으로 보여줍니다. Streamlit 리런 없이 이미 렌더링된 data-detail(JSON)만
# 읽어서 보여주는 방식이라 빠르고, 매 리런마다 다시 주입돼도 한 번만 초기화됩니다.
MOOD_DETAIL_JS = """
<script>
(function() {
    const doc = window.parent.document;
    if (doc.__moodDetailInit) return;
    doc.__moodDetailInit = true;

    const style = doc.createElement('style');
    style.textContent = `
        #mallang-mood-popup {
            position: fixed; width: 260px; max-height: 320px; overflow-y: auto;
            background: #fff; border: 1px solid #DCEEEC; border-radius: 16px;
            box-shadow: 0 12px 32px rgba(0,0,0,0.18); padding: 16px; padding-top: 30px;
            z-index: 999997; display: none; opacity: 0; transition: opacity 0.12s ease;
        }
        #mallang-mood-popup.open { display: block; opacity: 1; }
        #mallang-mood-popup::after {
            content: ''; position: absolute; width: 12px; height: 12px; background: #fff;
            border: 1px solid #DCEEEC; left: var(--arrow-left, 124px); margin-left: -6px;
        }
        #mallang-mood-popup.arrow-bottom::after {
            bottom: -7px; border-top: none; border-left: none;
            transform: rotate(45deg);
        }
        #mallang-mood-popup.arrow-top::after {
            top: -7px; border-bottom: none; border-right: none;
            transform: rotate(45deg);
        }
        #mallang-mood-popup-date {
            font-size: 0.85rem; font-weight: 700; color: #1C2B2A; margin-bottom: 8px;
            font-family: 'Pretendard','Malgun Gothic',-apple-system,sans-serif;
        }
        #mallang-mood-popup-close {
            position: absolute; top: 8px; right: 10px; border: none; background: none; cursor: pointer;
            font-size: 14px; color: #6B8C89; padding: 4px;
        }
        .mallang-mood-entry {
            padding: 7px 0; border-top: 1px solid #E7FBF8; font-size: 0.8rem; color: #1C2B2A;
            font-family: 'Pretendard','Malgun Gothic',-apple-system,sans-serif;
        }
        .mallang-mood-entry:first-of-type { border-top: none; }
        .mallang-mood-entry .t { font-weight: 700; color: #6B8C89; margin-right: 6px; }
        .mallang-mood-entry .memo { color: #6B8C89; margin-top: 2px; }
        #mallang-mood-popup-empty {
            font-size: 0.8rem; color: #6B8C89;
            font-family: 'Pretendard','Malgun Gothic',-apple-system,sans-serif;
        }
    `;
    doc.head.appendChild(style);

    const popup = doc.createElement('div');
    popup.id = 'mallang-mood-popup';
    popup.innerHTML =
        '<button id="mallang-mood-popup-close">\\u2715</button>' +
        '<div id="mallang-mood-popup-date"></div>' +
        '<div id="mallang-mood-popup-body"></div>';
    doc.body.appendChild(popup);

    const dateEl = popup.querySelector('#mallang-mood-popup-date');
    const bodyEl = popup.querySelector('#mallang-mood-popup-body');
    let activeCell = null;

    popup.querySelector('#mallang-mood-popup-close').addEventListener('click', function() {
        popup.classList.remove('open');
        activeCell = null;
    });

    function positionNear(cell) {
        const rect = cell.getBoundingClientRect();
        const margin = 10;
        popup.classList.remove('arrow-top', 'arrow-bottom');
        popup.style.left = '-9999px';
        popup.style.top = '-9999px';
        popup.classList.add('open');
        const pw = popup.offsetWidth;
        const ph = popup.offsetHeight;

        let left = rect.left + rect.width / 2 - pw / 2;
        left = Math.max(margin, Math.min(left, doc.documentElement.clientWidth - pw - margin));

        let top = rect.top - ph - margin;
        let arrowClass = 'arrow-bottom'; // 팝업이 칸 위에 있으면, 화살표는 팝업 아래쪽(칸을 가리킴)
        if (top < margin) {
            top = rect.bottom + margin;
            arrowClass = 'arrow-top'; // 위쪽에 자리가 없으면 칸 아래로, 화살표는 팝업 위쪽
        }
        top = Math.max(margin, Math.min(top, doc.documentElement.clientHeight - ph - margin));

        popup.style.left = left + 'px';
        popup.style.top = top + 'px';
        popup.classList.add(arrowClass);

        // 화살표는 항상 클릭한 칸 쪽을 가리키도록, 팝업 기준 x위치를 다시 맞춤
        const arrowLeft = Math.max(14, Math.min(rect.left + rect.width / 2 - left, pw - 14));
        popup.style.setProperty('--arrow-left', arrowLeft + 'px');
    }

    doc.addEventListener('click', function(e) {
        const cell = e.target.closest && e.target.closest('.mood-cell-hasdata');
        if (cell) {
            if (activeCell === cell && popup.classList.contains('open')) {
                // 같은 칸을 다시 클릭하면 닫기
                popup.classList.remove('open');
                activeCell = null;
                return;
            }
            let data;
            try { data = JSON.parse(cell.getAttribute('data-detail')); } catch (err) { return; }
            dateEl.textContent = data.date + (data.avg ? ' \\u00b7 ' + data.avg : '');
            if (data.entries && data.entries.length) {
                bodyEl.innerHTML = data.entries.map(function(en) {
                    return '<div class="mallang-mood-entry"><span class="t">' + en.time + '</span>' + en.label +
                        (en.memo ? '<div class="memo">' + en.memo + '</div>' : '') + '</div>';
                }).join('');
            } else {
                bodyEl.innerHTML = '<div id="mallang-mood-popup-empty">기록이 없어요.</div>';
            }
            positionNear(cell);
            activeCell = cell;
            return;
        }
        if (!popup.contains(e.target)) {
            popup.classList.remove('open');
            activeCell = null;
        }
    });
})();
</script>
"""
components.html(MOOD_DETAIL_JS, height=0, width=0)


# ==================== 옷 색상 팔레트 ====================
COLOR_PALETTE = {
    "빨강": ("❤️", "#FF6B6B"),
    "주황": ("🧡", "#FFA94D"),
    "노랑": ("💛", "#FFD43B"),
    "초록": ("💚", "#51CF66"),
    "하늘": ("🩵", "#74C0FC"),
    "파랑": ("💙", "#4DABF7"),
    "남색": ("💙", "#3B5BDB"),
    "보라": ("💜", "#B197FC"),
    "분홍": ("🩷", "#F783AC"),
    "갈색": ("🤎", "#A97155"),
    "베이지": ("🤎", "#E9DFC9"),
    "검정": ("🖤", "#343A40"),
    "흰색": ("🤍", "#F1F3F5"),
    "회색": ("🩶", "#ADB5BD"),
}
_LIGHT_COLOR_NAMES = {"흰색", "베이지", "노랑"}
_COLOR_SELECT_OPTIONS = [f"{emoji} {name}" for name, (emoji, _) in COLOR_PALETTE.items()]


def _color_name(raw) -> str:
    if not raw:
        return ""
    raw = str(raw).strip()
    parts = raw.split(" ", 1)
    return parts[-1] if len(parts) > 1 else parts[0]


def _color_hex(raw):
    name = _color_name(raw)
    hexcode = COLOR_PALETTE.get(name, (None, "#C9C9D9"))[1]
    text_color = "#20242A" if name in _LIGHT_COLOR_NAMES else "#FFFFFF"
    return hexcode, text_color


def _outfit_tag(icon: str, label, raw_color=None) -> str:
    if not label or (isinstance(label, float) and pd.isna(label)):
        return ""
    hexcode, text_color = _color_hex(raw_color)
    name = _color_name(raw_color)
    suffix = f" · {name}" if name else ""
    return (
        f'<span class="outfit-tag" style="background:{hexcode};color:{text_color};">'
        f"{icon} {label}{suffix}</span>"
    )


def render_outfit_list(df: pd.DataFrame):
    """옷 기록 목록 - 같은 날짜에 나뉘어 저장된 행들을 하나로 합쳐서 보여주고,
    삭제 시엔 그 날짜에 해당하는 원본 행을 전부 지웁니다."""
    order = st.selectbox(
        "정렬", ["최신순", "오래된순"], key="Outfits_sort_order",
        label_visibility="collapsed",
    )

    tmp = df.copy()
    tmp["_d"] = pd.to_datetime(tmp["날짜"], errors="coerce")
    tmp = tmp.dropna(subset=["_d"])

    groups: dict = {}
    for idx, row in tmp.iterrows():
        d = row["_d"].date()
        groups.setdefault(d, []).append((idx, row))

    dates = sorted(groups.keys(), reverse=(order == "최신순"))

    records = []
    index_lists = []
    for d in dates:
        items = groups[d]
        merged = _merge_day_rows([r for _, r in items])
        rec = {"날짜": d.strftime("%Y-%m-%d")}
        for col, icon in OUTFIT_COLS:
            val = merged.get(col, "")
            cname = _color_name(merged.get(f"{col}색상", "")) if val else ""
            rec[f"{icon} {col}"] = f"{val} ({cname})" if (val and cname) else (val or "")
        rec["메모"] = merged.get("메모", "")
        records.append(rec)
        index_lists.append([i for i, _ in items])

    display_df = pd.DataFrame(records)
    event = st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row",
        key="Outfits_table",
    )
    selected = list(event.selection.rows) if event and event.selection else []
    if selected:
        original_idx = []
        for pos in selected:
            original_idx.extend(index_lists[pos])
        if st.button(
            f"🗑️ 선택한 {len(selected)}개 날짜 기록 삭제",
            key="Outfits_delete_btn",
            use_container_width=True,
        ):
            storage.delete_rows("Outfits", original_idx)
            st.success("삭제했어요!")
            st.rerun()


def render_deletable_table(sheet_name: str, df: pd.DataFrame, sort_col: str = "날짜", transform=None):
    """날짜 정렬 옵션과 함께 표를 보여주고, 행을 선택해서 삭제할 수 있게 합니다."""
    order = st.selectbox(
        "정렬", ["최신순", "오래된순"], key=f"{sheet_name}_sort_order",
        label_visibility="collapsed",
    )
    sorted_df = df.sort_values(sort_col, ascending=(order == "오래된순"))
    display_df = transform(sorted_df) if transform else sorted_df

    event = st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row",
        key=f"{sheet_name}_table",
    )
    selected = list(event.selection.rows) if event and event.selection else []
    if selected:
        original_idx = display_df.iloc[selected].index.tolist()
        if st.button(
            f"🗑️ 선택한 {len(selected)}개 기록 삭제",
            key=f"{sheet_name}_delete_btn",
            use_container_width=True,
        ):
            storage.delete_rows(sheet_name, original_idx)
            st.success("삭제했어요!")
            st.rerun()


OUTFIT_COLS = [("상의", "👕"), ("하의", "👖"), ("가방", "👜"), ("양말", "🧦"), ("신발", "👟")]
OUTFIT_KEY_SUFFIX = {"상의": "top", "하의": "bottom", "가방": "bag", "양말": "socks", "신발": "shoes"}


def _start_outfit_edit(picked_date, row):
    """달력/목록에서 특정 날짜를 수정 모드로 진입시킵니다.

    폼 위젯(outfit_date 등)은 이 함수가 호출되는 시점(달력 버튼 클릭 처리)에는
    이미 이번 스크립트 실행에서 인스턴스화되어 있어서, 그 키를 바로 덮어쓰면
    "widget already instantiated" 오류가 납니다. 그래서 값을 별도의 대기(pending)
    상태에 저장해두고, 다음 렌더링에서 폼 위젯이 만들어지기 *전에* 적용합니다.
    """
    pending = {"outfit_date": picked_date}
    for col, _icon in OUTFIT_COLS:
        suffix = OUTFIT_KEY_SUFFIX[col]
        val = row.get(col, "")
        pending[f"outfit_{suffix}"] = val if val else None
        color_val = row.get(f"{col}색상", "")
        pending[f"outfit_{suffix}_color"] = color_val if color_val else None
    pending["outfit_memo"] = row.get("메모", "") or ""
    st.session_state["_outfit_edit_pending"] = pending
    st.session_state["outfit_edit_date"] = picked_date
    st.session_state["_scroll_to_outfit_form"] = True


def _merge_day_rows(rows) -> dict:
    """같은 날짜에 기록이 여러 번 나뉘어 저장된 경우(예: 상의만 먼저 기록하고
    나중에 하의를 따로 기록한 경우), 그 날의 모든 행을 합쳐서 하나로 보여줍니다."""
    merged: dict = {}
    memos = []
    for row in rows:
        for col, _icon in OUTFIT_COLS:
            val = row.get(col, "")
            if val and not (isinstance(val, float) and pd.isna(val)):
                merged[col] = val
                merged[f"{col}색상"] = row.get(f"{col}색상", "")
        memo = row.get("메모", "")
        if memo and not (isinstance(memo, float) and pd.isna(memo)) and str(memo).strip():
            memos.append(str(memo))
    merged["메모"] = " / ".join(memos)
    return merged


def render_outfit_calendar(df: pd.DataFrame):
    key = "outfit_cal_ym"
    if key not in st.session_state:
        today = date.today()
        st.session_state[key] = (today.year, today.month)
    year, month = st.session_state[key]

    nav_ctx = st.container(key="outfit_cal_nav")
    nav1, nav2, nav3 = nav_ctx.columns([1, 3, 1])
    with nav1:
        if st.button("◀", key="outfit_cal_prev", use_container_width=True):
            month -= 1
            if month == 0:
                month, year = 12, year - 1
            st.session_state[key] = (year, month)
            st.rerun()
    with nav2:
        st.markdown(f'<p class="cal-month-label">{year}년 {month}월</p>', unsafe_allow_html=True)
    with nav3:
        if st.button("▶", key="outfit_cal_next", use_container_width=True):
            month += 1
            if month == 13:
                month, year = 1, year + 1
            st.session_state[key] = (year, month)
            st.rerun()

    day_records = {}
    if not df.empty:
        tmp = df.copy()
        tmp["_d"] = pd.to_datetime(tmp["날짜"], errors="coerce").dt.date
        tmp = tmp.dropna(subset=["_d"])
        for _, row in tmp.iterrows():
            day_records.setdefault(row["_d"], []).append(row)

    weeks = cal_module.Calendar(firstweekday=6).monthdatescalendar(year, month)
    weekday_labels = ["일", "월", "화", "수", "목", "금", "토"]
    today = date.today()

    picked = st.session_state.get("outfit_cal_detail_pick")
    if picked is not None and (picked.year != year or picked.month != month):
        picked = None

    dot_styles = []
    with st.container(key="outfit_cal_grid"):
        header_cols = st.columns(7, gap="small")
        for hcol, wd in zip(header_cols, weekday_labels):
            hcol.markdown(f'<div class="cal-weekday">{wd}</div>', unsafe_allow_html=True)

        for week in weeks:
            wcols = st.columns(7, gap="small")
            for wcol, d in zip(wcols, week):
                in_month = d.month == month
                is_today = d == today
                marker = "__today" if is_today else ("__dim" if not in_month else "__norm")
                btn_key = f"outfit_cal_day_{d.isoformat()}{marker}"

                btn_label = str(d.day)
                help_text = None
                if d in day_records:
                    rec = _merge_day_rows(day_records[d])
                    worn = [(col, rec.get(col, "")) for col, _icon in OUTFIT_COLS if rec.get(col, "")]
                    if worn:
                        help_text = " · ".join(f"{col} {val}" for col, val in worn)
                        n = len(worn)
                        gradients = []
                        for i, (col, val) in enumerate(worn):
                            hexcode, _ = _color_hex(rec.get(f"{col}색상", ""))
                            x = 50 + (i - (n - 1) / 2) * 16
                            gradients.append(
                                f"radial-gradient(circle at {x:.0f}% 84%, {hexcode} 3px, transparent 3.5px)"
                            )
                        dot_styles.append(
                            f'div[class*="st-key-{btn_key}"] button {{'
                            f"background-image: {', '.join(gradients)};"
                            f"background-repeat: no-repeat; }}"
                        )

                with wcol:
                    if st.button(
                        btn_label, key=btn_key,
                        use_container_width=True, help=help_text,
                    ):
                        st.session_state["outfit_cal_detail_pick"] = d
                        st.rerun()

    if dot_styles:
        st.markdown(f"<style>{''.join(dot_styles)}</style>", unsafe_allow_html=True)

    month_dates = sorted(
        [d for d in day_records if d.year == year and d.month == month], reverse=True
    )
    if picked is None and month_dates:
        picked = month_dates[0]

    st.write("")
    if picked is None:
        st.caption("이 달엔 기록이 없어요. 날짜를 클릭하면 자세히 볼 수 있어요.")
    elif picked not in day_records:
        st.caption(f"📅 {picked.strftime('%Y-%m-%d (%a)')} · 이 날짜엔 기록이 없어요.")
    else:
        st.caption(f"📌 {picked.strftime('%Y-%m-%d (%a)')} · 달력에서 다른 날짜를 클릭하면 바뀌어요.")
        row = _merge_day_rows(day_records[picked])
        tags_html = "".join(
            _outfit_tag(icon, row.get(col, ""), row.get(f"{col}색상", ""))
            for col, icon in OUTFIT_COLS
        )
        if tags_html:
            st.markdown(f'<div style="margin:0.8rem 0;">{tags_html}</div>', unsafe_allow_html=True)
        if row.get("메모"):
            st.caption(f"📝 {row['메모']}")
        if len(day_records[picked]) > 1:
            st.caption(f"이 날짜에 기록이 {len(day_records[picked])}개 나뉘어 저장되어 있어요. 합쳐서 보여주는 중이에요.")
        original_positions = df.index[
            pd.to_datetime(df["날짜"], errors="coerce").dt.date == picked
        ].tolist()
        bcol1, bcol2 = st.columns(2, gap="small")
        with bcol1:
            if st.button("✏️ 이 날짜 수정", key="outfit_cal_edit_btn", use_container_width=True):
                _start_outfit_edit(picked, row)
                st.rerun()
        with bcol2:
            if st.button("🗑️ 이 날 기록 삭제", key="outfit_cal_delete_btn", use_container_width=True):
                storage.delete_rows("Outfits", original_positions)
                st.session_state.pop("outfit_cal_detail_pick", None)
                st.success("삭제했어요!")
                st.rerun()


# ==================== 기분 기록 (잔디밭 스타일 히트맵) ====================
MOOD_LABELS = {
    1: "😫 매우 안좋음",
    2: "🙁 안좋음",
    3: "😐 보통",
    4: "🙂 좋음",
    5: "😄 최고",
}
MOOD_COLORS = {
    1: "#E4EEEC",
    2: "#BEEAE3",
    3: "#7FDDD0",
    4: "#34D7BE",
    5: "#0F9C87",
}


def render_mood_calendar(df: pd.DataFrame):
    """옷 기록 달력처럼 ◀▶ 로 월을 넘겨보면서 그 달의 기분을 칸 색깔로 보여줍니다.
    칸을 클릭하면 그날 몇 시에 어떤 기분을 기록했는지 팝업으로 보여줘요."""
    key = "mood_cal_ym"
    if key not in st.session_state:
        today0 = date.today()
        st.session_state[key] = (today0.year, today0.month)
    year, month = st.session_state[key]

    nav_ctx = st.container(key="mood_cal_nav")
    nav1, nav2, nav3 = nav_ctx.columns([1, 3, 1])
    with nav1:
        if st.button("◀", key="mood_cal_prev", use_container_width=True):
            month -= 1
            if month == 0:
                month, year = 12, year - 1
            st.session_state[key] = (year, month)
            st.rerun()
    with nav2:
        st.markdown(f'<p class="cal-month-label">{year}년 {month}월</p>', unsafe_allow_html=True)
    with nav3:
        if st.button("▶", key="mood_cal_next", use_container_width=True):
            month += 1
            if month == 13:
                month, year = 1, year + 1
            st.session_state[key] = (year, month)
            st.rerun()

    today = date.today()
    day_scores: dict = {}
    day_entries: dict = {}
    tmp = df.copy()
    tmp["_d"] = pd.to_datetime(tmp["날짜"], errors="coerce").dt.date
    for _, row in tmp.dropna(subset=["_d"]).iterrows():
        try:
            score = int(row["기분"])
        except (ValueError, TypeError):
            continue
        d = row["_d"]
        day_scores.setdefault(d, []).append(score)
        day_entries.setdefault(d, []).append(
            {
                "time": str(row.get("시간", "") or "").strip(),
                "label": html.escape(MOOD_LABELS.get(score, "")),
                "memo": html.escape(str(row.get("메모", "") or "").strip()),
            }
        )
    mood_by_date = {d: round(sum(s) / len(s)) for d, s in day_scores.items() if s}
    for d in day_entries:
        day_entries[d].sort(key=lambda e: e["time"])

    weeks = cal_module.Calendar(firstweekday=6).monthdatescalendar(year, month)
    weekday_labels = ["일", "월", "화", "수", "목", "금", "토"]

    cells_html = "".join(f'<div class="cal-weekday">{wd}</div>' for wd in weekday_labels)
    for week in weeks:
        for d in week:
            classes = ["cal-cell"]
            if d.month != month:
                classes.append("cal-cell-dim")
            if d == today:
                classes.append("cal-cell-today")

            attrs = ""
            daynum_style = ""
            score = mood_by_date.get(d) if d <= today else None
            if score:
                scores = day_scores[d]
                color = MOOD_COLORS.get(score, MOOD_COLORS[3])
                avg_label = MOOD_LABELS.get(score, "")
                count_note = f" ({len(scores)}회 기록)" if len(scores) > 1 else ""
                title = f"{d.strftime('%Y-%m-%d')} · {avg_label}{count_note}"
                payload = html.escape(
                    json.dumps(
                        {"date": d.strftime("%Y-%m-%d"), "avg": avg_label + count_note, "entries": day_entries.get(d, [])},
                        ensure_ascii=False,
                    )
                )
                classes.append("mood-cell-hasdata")
                text_color = "#FFFFFF" if score >= 4 else "#1C2B2A"
                daynum_style = f' style="color:{text_color};"'
                attrs = f' style="background:{color};" title="{title}" data-detail="{payload}"'

            cells_html += (
                f'<div class="{" ".join(classes)}"{attrs}>'
                f'<span class="cal-daynum"{daynum_style}>{d.day}</span></div>'
            )

    st.markdown(f'<div class="cal-grid">{cells_html}</div>', unsafe_allow_html=True)

    legend_dots = "".join(
        f'<span class="mood-legend-dot" style="background:{MOOD_COLORS[s]};"></span>'
        for s in range(1, 6)
    )
    st.markdown(
        f'<div class="mood-legend"><span>별로</span>{legend_dots}<span>최고</span></div>',
        unsafe_allow_html=True,
    )

    recorded = tmp.dropna(subset=["_d"])
    streak = 0
    cur = today
    recorded_dates = set(mood_by_date.keys())
    while cur in recorded_dates:
        streak += 1
        cur -= timedelta(days=1)
    c1, c2 = st.columns(2, gap="medium")
    c1.metric("연속 기록", f"🔥 {streak}일")
    if not recorded.empty:
        try:
            avg = pd.to_numeric(recorded["기분"], errors="coerce").mean()
            c2.metric("평균 기분", f"{round(avg, 1)} / 5")
        except Exception:
            pass


# ==================== 사랑 고백 ====================
def render_love_notes(df: pd.DataFrame):
    order = st.selectbox(
        "정렬", ["최신순", "오래된순"], key="LoveNotes_sort_order",
        label_visibility="collapsed",
    )
    sorted_df = df.sort_values("날짜", ascending=(order == "오래된순"))
    for idx, row in sorted_df.iterrows():
        with st.container(border=True, key=f"love_note_{idx}"):
            c1, c2 = st.columns([6, 1])
            with c1:
                content = str(row.get("내용", "")).replace("<", "&lt;").replace(">", "&gt;")
                st.markdown(
                    f'<div><span class="love-note-date">💌 {row.get("날짜", "")}</span>'
                    f'<p class="love-note-text">{content}</p></div>',
                    unsafe_allow_html=True,
                )
            with c2:
                if st.button("🗑️", key=f"love_delete_{idx}"):
                    storage.delete_rows("LoveNotes", [idx])
                    st.success("삭제했어요!")
                    st.rerun()


# ==================== 헤더 (연결 상태 배지 포함) ====================
_mode = storage.storage_mode()
_badge_map = {
    "oauth": "🟢 저장 연결됨",
    "apps_script": "🟢 저장 연결됨",
    "gsheets": "🟢 저장 연결됨",
}
badge_text = _badge_map.get(_mode, "🟡 로컬 테스트 모드")

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-top">
            <div>
                <h1>🍡 말랑 다이어리</h1>
                <p>오늘의 옷차림, 기분, 소비, 습관을 한 곳에서 가볍게 기록해보세요.</p>
            </div>
            <span class="hero-badge">{badge_text}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
if _mode == "local":
    st.caption("앱을 재시작하면 기록이 사라질 수 있어요. SETUP_GUIDE.md 를 참고해서 구글 시트에 연결해보세요.")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["👕 옷 기록", "😊 기분 기록", "📚 책/영화", "💰 가계부", "🔥 습관 트래커", "💌 사랑고백"]
)

# ==================== 1. 옷 기록 ====================
with tab1:
    st.markdown('<div id="outfit-top-anchor"></div>', unsafe_allow_html=True)
    df = storage.load_df("Outfits")
    st.markdown(f'<p class="section-title">오늘 뭐 입었지? · 총 {len(df)}개 기록</p>', unsafe_allow_html=True)

    # 달력에서 "이 날짜 수정"을 누르면 값이 여기(위젯이 만들어지기 전)에서 반영돼요.
    _pending_edit = st.session_state.pop("_outfit_edit_pending", None)
    if _pending_edit:
        for _k, _v in _pending_edit.items():
            st.session_state[_k] = _v

    # 달력은 화면 아래쪽에 있어서, 거기서 "수정" 버튼을 눌러도 위쪽 폼이 바뀐 걸
    # 못 보고 지나치기 쉬워요. 폼이 있는 위치로 자동으로 스크롤해줍니다.
    if st.session_state.pop("_scroll_to_outfit_form", False):
        components.html(
            """
            <script>
            (function() {
                const doc = window.parent.document;
                const el = doc.getElementById('outfit-top-anchor');
                if (el) { el.scrollIntoView({behavior: 'smooth', block: 'start'}); }
            })();
            </script>
            """,
            height=0, width=0,
        )

    def _outfit_options(col: str):
        if df.empty or col not in df.columns:
            return []
        s = df[col].dropna().astype(str)
        s = s[s.str.strip() != ""]
        return s.value_counts().index.tolist()

    def _item_color_map(item_col: str, color_col: str) -> dict:
        if df.empty or item_col not in df.columns:
            return {}
        sub = df[[item_col, color_col]].dropna(subset=[item_col]) if color_col in df.columns else pd.DataFrame()
        m = {}
        for _, r in sub.iterrows():
            val = str(r[item_col]).strip()
            color = str(r.get(color_col, "") or "").strip()
            if val and color:
                m[val] = color  # 뒤에 나온(더 최근) 기록이 우선되도록 계속 덮어씀
        return m

    _COLOR_MAPS = {col: _item_color_map(col, f"{col}색상") for col, _ in OUTFIT_COLS}

    def _on_item_change(col: str):
        suffix = OUTFIT_KEY_SUFFIX[col]
        val = st.session_state.get(f"outfit_{suffix}")
        if val:
            matched = _COLOR_MAPS[col].get(str(val).strip())
            if matched:
                st.session_state[f"outfit_{suffix}_color"] = matched

    def _clear_outfit_form_state():
        for _col, _ in OUTFIT_COLS:
            _suffix = OUTFIT_KEY_SUFFIX[_col]
            st.session_state.pop(f"outfit_{_suffix}", None)
            st.session_state.pop(f"outfit_{_suffix}_color", None)
        st.session_state.pop("outfit_memo", None)
        st.session_state.pop("outfit_date", None)
        st.session_state.pop("outfit_edit_date", None)
        st.session_state.pop("_outfit_edit_pending", None)

    edit_date = st.session_state.get("outfit_edit_date")
    if edit_date:
        ec1, ec2 = st.columns([5, 1])
        with ec1:
            st.info(f"✏️ {edit_date} 기록을 수정하는 중이에요. 저장하면 그날 기존 기록을 덮어써요.")
        with ec2:
            if st.button("취소", key="outfit_edit_cancel", use_container_width=True):
                _clear_outfit_form_state()
                st.rerun()

    with st.expander("✏️ 기록하기", expanded=True, key="outfit_form_exp"):
        with st.container(border=True, key="outfit_form_card"):
            d = st.date_input("날짜", value=date.today(), key="outfit_date")

            st.markdown('<p class="sub-label">아이템</p>', unsafe_allow_html=True)
            c1, c2, c3, c4, c5 = st.columns(5, gap="small")
            with c1:
                top = st.selectbox(
                    "상의", options=_outfit_options("상의"), index=None,
                    placeholder="선택/입력", accept_new_options=True, key="outfit_top",
                    on_change=_on_item_change, args=("상의",),
                )
            with c2:
                bottom = st.selectbox(
                    "하의", options=_outfit_options("하의"), index=None,
                    placeholder="선택/입력", accept_new_options=True, key="outfit_bottom",
                    on_change=_on_item_change, args=("하의",),
                )
            with c3:
                bag = st.selectbox(
                    "가방", options=_outfit_options("가방"), index=None,
                    placeholder="선택/입력", accept_new_options=True, key="outfit_bag",
                    on_change=_on_item_change, args=("가방",),
                )
            with c4:
                socks = st.selectbox(
                    "양말", options=_outfit_options("양말"), index=None,
                    placeholder="선택/입력", accept_new_options=True, key="outfit_socks",
                    on_change=_on_item_change, args=("양말",),
                )
            with c5:
                shoes = st.selectbox(
                    "신발", options=_outfit_options("신발"), index=None,
                    placeholder="선택/입력", accept_new_options=True, key="outfit_shoes",
                    on_change=_on_item_change, args=("신발",),
                )

            st.markdown('<p class="sub-label">색상 (선택 · 같은 아이템을 다시 고르면 자동으로 채워져요)</p>', unsafe_allow_html=True)
            cc1, cc2, cc3, cc4, cc5 = st.columns(5, gap="small")
            with cc1:
                top_color = st.selectbox(
                    "상의 색", options=_COLOR_SELECT_OPTIONS, index=None,
                    placeholder="색상", accept_new_options=True, key="outfit_top_color",
                )
            with cc2:
                bottom_color = st.selectbox(
                    "하의 색", options=_COLOR_SELECT_OPTIONS, index=None,
                    placeholder="색상", accept_new_options=True, key="outfit_bottom_color",
                )
            with cc3:
                bag_color = st.selectbox(
                    "가방 색", options=_COLOR_SELECT_OPTIONS, index=None,
                    placeholder="색상", accept_new_options=True, key="outfit_bag_color",
                )
            with cc4:
                socks_color = st.selectbox(
                    "양말 색", options=_COLOR_SELECT_OPTIONS, index=None,
                    placeholder="색상", accept_new_options=True, key="outfit_socks_color",
                )
            with cc5:
                shoes_color = st.selectbox(
                    "신발 색", options=_COLOR_SELECT_OPTIONS, index=None,
                    placeholder="색상", accept_new_options=True, key="outfit_shoes_color",
                )

            st.caption("💡 목록에 없는 걸 새로 입력했다면, 다음 칸으로 넘어가기 전에 꼭 Enter를 눌러 확정해주세요.")
            memo = st.text_input("메모 (선택)", placeholder="예: 좀 더웠음", key="outfit_memo")
            submit_label = "💾 수정 완료" if edit_date else "✏️ 기록하기"
            submitted = st.button(submit_label, use_container_width=True, type="primary", key="outfit_submit_btn")
            if submitted:
                if any([top, bottom, bag, socks, shoes]):
                    if edit_date:
                        existing_idx = df.index[
                            pd.to_datetime(df["날짜"], errors="coerce").dt.date == edit_date
                        ].tolist()
                        if existing_idx:
                            storage.delete_rows("Outfits", existing_idx)
                    storage.append_row(
                        "Outfits",
                        {
                            "날짜": str(d),
                            "상의": top or "",
                            "하의": bottom or "",
                            "가방": bag or "",
                            "양말": socks or "",
                            "신발": shoes or "",
                            "메모": memo,
                            "상의색상": top_color or "",
                            "하의색상": bottom_color or "",
                            "가방색상": bag_color or "",
                            "양말색상": socks_color or "",
                            "신발색상": shoes_color or "",
                        },
                    )
                    _clear_outfit_form_state()
                    st.success("기록했어요!")
                    st.rerun()
                else:
                    st.warning("적어도 한 항목은 입력해주세요.")

    st.write("")
    with st.container(border=True, key="outfit_results"):
        if df.empty:
            st.caption("아직 기록이 없어요. 첫 옷차림을 기록해보세요 👗")
        else:
            cal_tab, list_tab = st.tabs(["📅 달력", "📋 목록"])
            with cal_tab:
                render_outfit_calendar(df)
            with list_tab:
                render_outfit_list(df)

# ==================== 2. 기분 기록 ====================
with tab2:
    df = storage.load_df("Moods")
    st.markdown('<p class="section-title">지금 기분은 어때요?</p>', unsafe_allow_html=True)
    st.caption("하루에 여러 번 기록할 수 있어요. 예: 출근할 때, 점심 먹고, 퇴근할 때")

    with st.expander("✏️ 기록하기", expanded=True, key="mood_form_exp"):
        with st.form("mood_form", clear_on_submit=False):
            c1, c2 = st.columns(2, gap="medium")
            with c1:
                mood_date = st.date_input("날짜", value=date.today(), key="mood_date")
            with c2:
                mood_time = st.time_input(
                    "시간", value=datetime.now().time().replace(second=0, microsecond=0),
                    step=60, key="mood_time",
                )
            mood_score = st.radio(
                "기분",
                options=[1, 2, 3, 4, 5],
                format_func=lambda v: MOOD_LABELS[v],
                index=2,
                horizontal=True,
                key="mood_score",
            )
            mood_memo = st.text_input("메모 (선택)", placeholder="예: 회의 많아서 힘들었음", key="mood_memo")
            mood_submitted = st.form_submit_button("✏️ 기록하기", use_container_width=True, type="primary")
            if mood_submitted:
                time_str = mood_time.strftime("%H:%M")
                # 같은 날짜+시간에 이미 기록이 있으면 덮어씁니다 (그 외엔 하루에 여러 개 쌓여요).
                existing_idx = df.index[
                    (pd.to_datetime(df["날짜"], errors="coerce").dt.date == mood_date)
                    & (df["시간"].astype(str) == time_str)
                ].tolist() if not df.empty else []
                if existing_idx:
                    storage.delete_rows("Moods", existing_idx)
                storage.append_row(
                    "Moods",
                    {"날짜": str(mood_date), "시간": time_str, "기분": mood_score, "메모": mood_memo},
                )
                st.success("기록했어요!")
                st.rerun()

    st.write("")
    with st.container(border=True, key="mood_results"):
        if df.empty:
            st.caption("아직 기록이 없어요. 오늘 기분부터 남겨보세요 🙂")
        else:
            render_mood_calendar(df)
            st.write("")
            render_deletable_table("Moods", df)

# ==================== 3. 책/영화 기록 ====================
with tab3:
    df = storage.load_df("Media")
    st.markdown(f'<p class="section-title">책 / 영화 기록 · 총 {len(df)}개 기록</p>', unsafe_allow_html=True)

    with st.expander("✏️ 기록하기", expanded=True, key="media_form_exp"):
        with st.form("media_form", clear_on_submit=True):
            c1, c2, c3 = st.columns([1, 1, 2], gap="medium")
            with c1:
                d = st.date_input("날짜", value=date.today(), key="media_date")
            with c2:
                kind = st.radio("종류", ["책", "영화"], horizontal=True, key="media_kind")
            with c3:
                title = st.text_input("제목", key="media_title")
            rating = st.slider("별점", 1, 5, 3, key="media_rating")
            review = st.text_area("감상평 (선택)", key="media_review")
            submitted = st.form_submit_button("✏️ 기록하기", use_container_width=True, type="primary")
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
    with st.container(border=True, key="media_results"):
        if not df.empty:
            col1, col2, col3 = st.columns(3, gap="medium")
            col1.metric("총 기록 수", len(df))
            try:
                col2.metric("평균 별점", f"{round(pd.to_numeric(df['별점']).mean(), 1)} ⭐")
            except Exception:
                pass
            col3.metric("책 / 영화", f"{(df['종류']=='책').sum()} / {(df['종류']=='영화').sum()}")
            render_deletable_table("Media", df)
        else:
            st.caption("아직 기록이 없어요. 최근에 본 책이나 영화를 남겨보세요 🎬")

# ==================== 4. 가계부 ====================
with tab4:
    df = storage.load_df("Expenses")
    st.markdown(f'<p class="section-title">가계부 · 총 {len(df)}건</p>', unsafe_allow_html=True)

    with st.expander("✏️ 기록하기", expanded=True, key="expense_form_exp"):
        with st.form("expense_form", clear_on_submit=True):
            c1, c2, c3 = st.columns([1, 1, 1], gap="medium")
            with c1:
                d = st.date_input("날짜", value=date.today(), key="expense_date")
            with c2:
                category = st.selectbox(
                    "카테고리", ["식비", "교통", "쇼핑", "문화생활", "고정비", "기타"], key="expense_cat"
                )
            with c3:
                amount = st.number_input("금액", min_value=0, step=1000, key="expense_amount")
            memo = st.text_input("메모 (선택)", key="expense_memo")
            submitted = st.form_submit_button("✏️ 기록하기", use_container_width=True, type="primary")
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
    with st.container(border=True, key="expense_results"):
        if not df.empty:
            df["금액"] = pd.to_numeric(df["금액"], errors="coerce")
            col1, col2 = st.columns(2, gap="medium")
            col1.metric("총 지출", f"{int(df['금액'].sum()):,}원")
            col2.metric("이번 기록 건수", len(df))
            chart_df = df.groupby("카테고리")["금액"].sum()
            st.bar_chart(chart_df, color="#2DD4BF")
            render_deletable_table("Expenses", df)
        else:
            st.caption("아직 기록이 없어요. 오늘 쓴 돈을 남겨보세요 💸")

# ==================== 5. 습관 트래커 ====================
with tab5:
    df = storage.load_df("Habits")
    habit_count = df["습관"].dropna().nunique() if not df.empty else 0
    st.markdown(f'<p class="section-title">습관 트래커 · {habit_count}개 습관 관리 중</p>', unsafe_allow_html=True)

    with st.expander("✏️ 기록하기", expanded=True, key="habit_form_exp"):
        with st.form("habit_form", clear_on_submit=True):
            c1, c2, c3 = st.columns([1, 2, 1], gap="medium")
            with c1:
                d = st.date_input("날짜", value=date.today(), key="habit_date")
            with c2:
                habit = st.text_input("습관 이름", placeholder="예: 물 마시기, 운동, 독서", key="habit_name")
            with c3:
                done = st.checkbox("완료했어요", value=True, key="habit_done")
            submitted = st.form_submit_button("✏️ 기록하기", use_container_width=True, type="primary")
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
    with st.container(border=True, key="habit_results"):
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
            render_deletable_table("Habits", df)
        else:
            st.caption("아직 기록이 없어요. 오늘부터 만들고 싶은 습관을 기록해보세요 💪")

# ==================== 6. 사랑 고백 ====================
with tab6:
    df = storage.load_df("LoveNotes")
    st.markdown(f'<p class="section-title">남편에게 전하는 마음 · 총 {len(df)}개</p>', unsafe_allow_html=True)

    with st.expander("✏️ 기록하기", expanded=True, key="love_form_exp"):
        with st.form("love_form", clear_on_submit=True):
            love_date = st.date_input("날짜", value=date.today(), key="love_date")
            love_text = st.text_area(
                "오늘의 사랑 고백 💌",
                placeholder="예: 오늘 아침에 커피 타준 거 너무 고마웠어. 사랑해 ❤️",
                key="love_text", height=100,
            )
            love_submitted = st.form_submit_button("💌 마음 전하기", use_container_width=True, type="primary")
            if love_submitted:
                if love_text.strip():
                    storage.append_row("LoveNotes", {"날짜": str(love_date), "내용": love_text})
                    st.success("기록했어요! 오늘도 사랑이 +1 됐어요 💕")
                    st.rerun()
                else:
                    st.warning("내용을 입력해주세요.")

    st.write("")
    with st.container(border=True, key="love_results"):
        if df.empty:
            st.caption("아직 기록이 없어요. 오늘의 사랑을 첫 줄로 남겨보세요 💌")
        else:
            render_love_notes(df)


# ==================== 모바일: 기록하기 폼 기본 접힘 ====================
# 좁은 화면(≤640px)에서는 "기록하기" expander들을 처음 로딩 시 한 번만 자동으로
# 접어줌(목록을 보기 편하게). 사용자가 직접 펼치면 그 뒤로는 리런돼도 다시
# 강제로 접지 않음 - 페이지를 완전히 새로고침해야 다시 적용됨.
EXPANDER_MOBILE_JS = """
<script>
(function() {
    const doc = window.parent.document;
    if (doc.__expMobileCollapseInit) return;
    doc.__expMobileCollapseInit = true;

    // 탭 안에 있는 expander는 활성 탭이 아니면 화면에 안 보이는 상태(display:none)라
    // offsetParent로 "펼쳐져있는지" 판단하면 항상 닫힌 것처럼 오판해서 못 접는 문제가
    // 있었음. 대신 모든 기록하기 expander는 파이썬 쪽에서 항상 expanded=True로
    // 시작한다는 걸 이미 알고 있으니, 보이는지 여부와 상관없이 무조건 한 번씩 클릭.
    function collapseIfMobile() {
        const w = window.parent.innerWidth || doc.documentElement.clientWidth;
        if (w > 640) { return true; }
        const expanders = doc.querySelectorAll('div[data-testid="stExpander"]');
        if (expanders.length < 6) return false; // 6개 탭 폼이 다 마운트될 때까지 대기
        expanders.forEach(function(exp) {
            if (exp.__mallangCollapsed) return;
            exp.__mallangCollapsed = true;
            const header = exp.querySelector('summary') || exp.firstElementChild;
            if (header) header.click();
        });
        return true;
    }

    let tries = 0;
    const timer = setInterval(function() {
        tries++;
        if (collapseIfMobile() || tries > 25) clearInterval(timer);
    }, 200);
})();
</script>
"""
components.html(EXPANDER_MOBILE_JS, height=0, width=0)
