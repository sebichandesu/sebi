"""
저장 모듈 - 우선순위대로 저장 방식을 자동 선택합니다.

1) OAuth 모드 (추천, 가장 안정적)
   secrets.toml 에 [google_oauth] (client_id/client_secret/refresh_token) + sheet_id 가 있으면
   구글 정식 Sheets API를 OAuth로 직접 호출 (Apps Script보다 자동화 접근에 훨씬 안정적)

2) Apps Script 모드 (GCP 콘솔 필요 없지만, 가끔 구글이 자동화 요청을 차단할 수 있음)
   secrets.toml 에 apps_script_url / apps_script_key 가 있으면
   구글 시트에 붙인 Apps Script 웹앱을 통해 저장

3) Google Sheets(서비스 계정) 모드
   secrets.toml 에 gcp_service_account / sheet_id 가 있으면
   gspread로 구글 시트에 직접 저장 (GCP 서비스 계정 키가 있어야 함)

4) 로컬 CSV 모드 (기본값, 아무 설정 없을 때)
   data/ 폴더에 CSV로 저장 (테스트용, 영구 저장 아님)
"""
import os

try:
    # 회사 네트워크처럼 SSL 트래픽을 검사하는 프록시 환경에서도
    # 윈도우/맥 OS가 신뢰하는 인증서를 그대로 쓰도록 해줍니다.
    import truststore

    truststore.inject_into_ssl()
except Exception:
    pass

import pandas as pd
import requests
import streamlit as st

DATA_DIR = "data"

SHEET_SCHEMAS = {
    # 색상 컬럼(*색상)은 뒤에 추가된 것으로, 기존 시트 데이터의 컬럼 위치가
    # 바뀌지 않도록 항상 맨 뒤에 붙입니다 (헤더 자동 보정 로직과 호환).
    "Outfits": [
        "날짜", "상의", "하의", "가방", "양말", "신발", "메모",
        "상의색상", "하의색상", "가방색상", "양말색상", "신발색상",
    ],
    "Media": ["날짜", "종류", "제목", "별점", "감상평"],
    "Expenses": ["날짜", "카테고리", "금액", "메모"],
    "Habits": ["날짜", "습관", "완료"],
    "Moods": ["날짜", "시간", "기분", "메모"],
    "LoveNotes": ["날짜", "내용"],
}


def _use_oauth() -> bool:
    try:
        return "google_oauth" in st.secrets and "sheet_id" in st.secrets
    except Exception:
        return False


def _use_apps_script() -> bool:
    try:
        return "apps_script_url" in st.secrets and "apps_script_key" in st.secrets
    except Exception:
        return False


def _use_gsheets() -> bool:
    try:
        return "gcp_service_account" in st.secrets and "sheet_id" in st.secrets
    except Exception:
        return False


def storage_mode() -> str:
    if _use_oauth():
        return "oauth"
    if _use_apps_script():
        return "apps_script"
    if _use_gsheets():
        return "gsheets"
    return "local"


def is_gsheets_mode() -> bool:
    return _use_oauth() or _use_apps_script() or _use_gsheets()


# 일부 회사 네트워크 보안 프록시는 브라우저가 아닌 요청(예: 파이썬 requests 기본 User-Agent)을
# 차단하거나 가로채서 빈 응답/로그인 페이지를 돌려줍니다. 브라우저처럼 보이는 헤더를 붙여줍니다.
_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
}


def _parse_apps_script_response(res):
    try:
        return res.json()
    except ValueError:
        snippet = (res.text or "")[:200]
        raise RuntimeError(
            f"Apps Script가 JSON이 아닌 응답을 보냈어요 (상태코드 {res.status_code}). "
            f"응답 일부: {snippet!r}"
        )


def _apps_script_get(sheet_name: str, retries: int = 2):
    url = st.secrets["apps_script_url"]
    key = st.secrets["apps_script_key"]
    last_err = None
    for attempt in range(retries + 1):
        try:
            res = requests.get(
                url,
                params={"sheet": sheet_name, "key": key},
                headers=_BROWSER_HEADERS,
                timeout=10,
            )
            res.raise_for_status()
            return _parse_apps_script_response(res)
        except Exception as e:
            last_err = e
    raise last_err


def _apps_script_post(sheet_name: str, row: dict, retries: int = 2):
    url = st.secrets["apps_script_url"]
    key = st.secrets["apps_script_key"]
    payload = {"sheet": sheet_name, "key": key, "row": row}
    last_err = None
    for attempt in range(retries + 1):
        try:
            res = requests.post(
                url, json=payload, headers=_BROWSER_HEADERS, timeout=10
            )
            res.raise_for_status()
            try:
                return _parse_apps_script_response(res)
            except RuntimeError:
                return {"ok": True, "note": "response was not JSON, assumed saved"}
        except Exception as e:
            last_err = e
    raise last_err


@st.cache_resource
def _get_gspread_client():
    import gspread

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    if _use_oauth():
        from google.oauth2.credentials import Credentials

        o = st.secrets["google_oauth"]
        creds = Credentials(
            token=None,
            refresh_token=o["refresh_token"],
            client_id=o["client_id"],
            client_secret=o["client_secret"],
            token_uri="https://oauth2.googleapis.com/token",
            scopes=scopes,
        )
        return gspread.authorize(creds)

    from google.oauth2.service_account import Credentials

    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=scopes
    )
    return gspread.authorize(creds)


def _get_worksheet_uncached(sheet_name: str):
    client = _get_gspread_client()
    sh = client.open_by_key(st.secrets["sheet_id"])
    expected_headers = SHEET_SCHEMAS[sheet_name]
    try:
        ws = sh.worksheet(sheet_name)
    except Exception:
        ws = sh.add_worksheet(
            title=sheet_name, rows=2000, cols=len(expected_headers)
        )
        ws.append_row(expected_headers)
        return ws

    # 스키마(컬럼 구성)가 바뀐 경우, 기존 시트의 헤더 행만 최신 컬럼명으로 맞춰줍니다.
    # (기존 데이터 행은 그대로 두고 헤더만 갱신 - 열이 늘어난 경우 예전 값은 앞쪽 컬럼에 남아있습니다)
    try:
        current_headers = ws.row_values(1)
    except Exception:
        current_headers = []
    if current_headers != expected_headers:
        ws.update("A1", [expected_headers])
    return ws


# 시트/헤더 조회(open_by_key, worksheet 찾기, 헤더 확인)는 매 API 호출마다 반복하면
# 구글 시트 API의 분당 읽기 한도(기본 60회/분)를 금방 넘길 수 있어요. 워크시트 객체
# 자체를 잠깐 캐싱해서 같은 시트를 반복해서 여는 것을 줄입니다.
@st.cache_resource(ttl=120, show_spinner=False)
def _get_worksheet(sheet_name: str):
    return _get_worksheet_uncached(sheet_name)


def _local_path(sheet_name: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{sheet_name}.csv")


# 옷/기분/가계부 등 폼에서 아이템을 하나씩 고를 때마다(색상 자동완성 등) 화면이
# 다시 그려지는데, 그때마다 매번 구글 시트를 새로 읽으면 API 읽기 한도를 순식간에
# 넘겨버려요(429 Quota exceeded). 짧은 시간(20초) 동안은 캐시된 값을 재사용하고,
# append_row/delete_rows로 실제 데이터가 바뀔 때만 캐시를 비워서 최신 데이터를 다시 읽습니다.
@st.cache_data(ttl=20, show_spinner=False)
def load_df(sheet_name: str) -> pd.DataFrame:
    columns = SHEET_SCHEMAS[sheet_name]

    if _use_oauth() or _use_gsheets():
        try:
            ws = _get_worksheet(sheet_name)
            records = ws.get_all_records()
        except Exception as e:
            st.error(f"구글 시트에서 데이터를 불러오지 못했어요: {e}")
            return pd.DataFrame(columns=columns)
        if not records:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame(records)

    if _use_apps_script():
        try:
            records = _apps_script_get(sheet_name)
        except Exception as e:
            st.error(f"Apps Script에서 데이터를 불러오지 못했어요: {e}")
            return pd.DataFrame(columns=columns)
        if not records:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame(records)

    path = _local_path(sheet_name)
    if not os.path.exists(path):
        return pd.DataFrame(columns=columns)
    return pd.read_csv(path)


def append_row(sheet_name: str, row: dict):
    columns = SHEET_SCHEMAS[sheet_name]

    if _use_oauth() or _use_gsheets():
        row_values = [row.get(c, "") for c in columns]
        ws = _get_worksheet(sheet_name)
        ws.append_row(row_values)
        load_df.clear()
        return

    if _use_apps_script():
        try:
            _apps_script_post(sheet_name, row)
        except Exception as e:
            st.warning(
                f"저장 확인 응답을 못 받았어요 (구글 쪽 일시적 문제일 수 있어요). "
                f"구글 시트를 열어서 실제로 저장됐는지 확인해보세요. ({e})"
            )
        load_df.clear()
        return

    row_values = [row.get(c, "") for c in columns]
    path = _local_path(sheet_name)
    df = load_df(sheet_name)
    new_row = pd.DataFrame([row_values], columns=columns)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(path, index=False)
    load_df.clear()


def delete_rows(sheet_name: str, indices):
    """indices: load_df()가 반환한 DataFrame의 (0부터 시작하는) 행 위치 목록."""
    indices = sorted(set(int(i) for i in indices), reverse=True)
    if not indices:
        return

    if _use_oauth() or _use_gsheets():
        ws = _get_worksheet(sheet_name)
        # 시트 1행은 헤더이므로, 데이터 i번째 행(0-base)은 실제 시트의 (i+2)번째 행
        for i in indices:
            ws.delete_rows(i + 2)
        load_df.clear()
        return

    if _use_apps_script():
        st.warning("Apps Script 모드에서는 삭제 기능이 아직 지원되지 않아요.")
        return

    columns = SHEET_SCHEMAS[sheet_name]
    path = _local_path(sheet_name)
    df = load_df(sheet_name)
    df = df.drop(df.index[indices]).reset_index(drop=True)
    df.to_csv(path, index=False)
    load_df.clear()
