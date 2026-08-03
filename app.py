import calendar as cal_module

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
from datetime import date, timedelta

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
    font-weight: 500;
    font-size: 0.88rem;
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

/* 모바일 대응 */
@media (max-width: 640px) {
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 1.4rem;
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
    div[data-testid="stForm"] {
        padding: 1.2rem 1.1rem 0.6rem 1.1rem;
    }
    .cal-cell {
        min-height: 46px;
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

    nav1, nav2, nav3 = st.columns([1, 3, 1])
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

    grid_html = '<div class="cal-grid">'
    for wd in weekday_labels:
        grid_html += f'<div class="cal-weekday">{wd}</div>'
    for week in weeks:
        for d in week:
            in_month = d.month == month
            is_today = d == today
            cls = "cal-cell"
            if not in_month:
                cls += " cal-cell-dim"
            if is_today:
                cls += " cal-cell-today"
            dots = ""
            if d in day_records:
                rec = _merge_day_rows(day_records[d])
                for col, _icon in OUTFIT_COLS:
                    val = rec.get(col, "")
                    if val:
                        hexcode, _ = _color_hex(rec.get(f"{col}색상", ""))
                        dots += f'<span class="cal-dot" style="background:{hexcode};" title="{col}: {val}"></span>'
            grid_html += f'<div class="{cls}"><span class="cal-daynum">{d.day}</span><div class="cal-dots">{dots}</div></div>'
    grid_html += "</div>"
    st.markdown(grid_html, unsafe_allow_html=True)

    month_dates = sorted(
        [d for d in day_records if d.year == year and d.month == month], reverse=True
    )
    if month_dates:
        picked = st.selectbox(
            "상세히 볼 날짜",
            options=month_dates,
            format_func=lambda d: d.strftime("%Y-%m-%d (%a)"),
            key="outfit_cal_detail_pick",
        )
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
        if st.button("🗑️ 이 날 기록 삭제", key="outfit_cal_delete_btn"):
            storage.delete_rows("Outfits", original_positions)
            st.success("삭제했어요!")
            st.rerun()
    else:
        st.caption("이 달엔 기록이 없어요.")


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

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["👕 옷 기록", "😂 짤 뽑기", "📚 책/영화", "💰 가계부", "🔥 습관 트래커"]
)

# ==================== 1. 옷 기록 ====================
with tab1:
    df = storage.load_df("Outfits")
    st.markdown(f'<p class="section-title">오늘 뭐 입었지? · 총 {len(df)}개 기록</p>', unsafe_allow_html=True)

    def _outfit_options(col: str):
        if df.empty or col not in df.columns:
            return []
        s = df[col].dropna().astype(str)
        s = s[s.str.strip() != ""]
        return s.value_counts().index.tolist()

    with st.form("outfit_form", clear_on_submit=True):
        d = st.date_input("날짜", value=date.today(), key="outfit_date")

        st.markdown('<p class="sub-label">아이템</p>', unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns(5, gap="small")
        with c1:
            top = st.selectbox(
                "상의", options=_outfit_options("상의"), index=None,
                placeholder="선택/입력", accept_new_options=True, key="outfit_top",
            )
        with c2:
            bottom = st.selectbox(
                "하의", options=_outfit_options("하의"), index=None,
                placeholder="선택/입력", accept_new_options=True, key="outfit_bottom",
            )
        with c3:
            bag = st.selectbox(
                "가방", options=_outfit_options("가방"), index=None,
                placeholder="선택/입력", accept_new_options=True, key="outfit_bag",
            )
        with c4:
            socks = st.selectbox(
                "양말", options=_outfit_options("양말"), index=None,
                placeholder="선택/입력", accept_new_options=True, key="outfit_socks",
            )
        with c5:
            shoes = st.selectbox(
                "신발", options=_outfit_options("신발"), index=None,
                placeholder="선택/입력", accept_new_options=True, key="outfit_shoes",
            )

        st.markdown('<p class="sub-label">색상 (선택)</p>', unsafe_allow_html=True)
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
        submitted = st.form_submit_button("✏️ 기록하기", use_container_width=True, type="primary")
        if submitted:
            if any([top, bottom, bag, socks, shoes]):
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

# ==================== 2. 짤 뽑기 ====================
with tab2:
    st.markdown('<p class="section-title">기분 전환이 필요할 때 😊</p>', unsafe_allow_html=True)

    import random

    _IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp")
    _MEME_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
    }
    # 기본(영어권) + 한국 관련 서브레딧을 섞어서 랜덤으로 골라요.
    # (레딧 기반이라 완전한 국내 짤방 느낌은 아니지만, 최소한 한국 관련 짤도 섞여 나와요)
    _MEME_SUBREDDITS = [
        "memes", "dankmemes", "me_irl",
        "KoreanMemes", "hanguk", "hanguk", "KoreanMemes",
    ]

    def _fetch_meme(max_tries: int = 3):
        st.session_state["meme_error"] = None
        last_err = None
        for _ in range(max_tries):
            sub = random.choice(_MEME_SUBREDDITS)
            try:
                res = requests.get(
                    f"https://meme-api.com/gimme/{sub}", timeout=6, headers=_MEME_HEADERS
                )
                res.raise_for_status()
                data = res.json()
            except Exception as e:
                last_err = f"{type(e).__name__}: {e}"
                continue
            url = (data.get("url") or "").lower()
            if url.endswith(_IMAGE_EXTS):
                st.session_state["meme"] = data
                return
            last_err = "이미지 형식이 아닌 결과(동영상 등)라 건너뜀"
        # 여기까지 왔으면 전부 실패
        st.session_state["meme"] = None
        st.session_state["meme_error"] = last_err

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
        err = st.session_state.get("meme_error")
        if err:
            st.caption(f"오류 내용: {err}")

# ==================== 3. 책/영화 기록 ====================
with tab3:
    df = storage.load_df("Media")
    st.markdown(f'<p class="section-title">책 / 영화 기록 · 총 {len(df)}개 기록</p>', unsafe_allow_html=True)

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
