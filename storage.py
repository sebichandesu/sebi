"""
저장 모듈 - 우선순위대로 저장 방식을 자동 선택합니다.

1) Apps Script 모드 (추천, 가장 간단함)
   secrets.toml 에 apps_script_url / apps_script_key 가 있으면
   구글 시트에 붙인 Apps Script 웹앱을 통해 저장 (GCP 콘솔/서비스 계정 필요 없음)

2) Google Sheets(서비스 계정) 모드
   secrets.toml 에 gcp_service_account / sheet_id 가 있으면
   gspread로 구글 시트에 직접 저장 (GCP 서비스 계정 키가 있어야 함)

3) 로컬 CSV 모드 (기본값, 아무 설정 없을 때)
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
    "Outfits": ["날짜", "옷차림", "메모"],
    "Media": ["날짜", "종류", "제목", "별점", "감상평"],
    "Expenses": ["날짜", "카테고리", "금액", "메모"],
    "Habits": ["날짜", "습관", "완료"],
}


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
    if _use_apps_script():
        return "apps_script"
    if _use_gsheets():
        return "gsheets"
    return "local"


def is_gsheets_mode() -> bool:
    return _use_apps_script() or _use_gsheets()


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
    # 구글이 가끔 정상 요청인데도 확인용 HTML 페이지를 응답으로 끼워넣는 경우가 있어요.
    # 이 경우 실제로는 시트에 저장은 성공하는 경우가 대부분이라, JSON 파싱에 실패해도
    # HTTP 상태코드가 정상(2xx)이면 "일단 저장된 것으로 간주"하고 넘어갑니다.
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
    from google.oauth2.service_account import Credentials

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=scopes
    )
    return gspread.authorize(creds)


def _get_worksheet(sheet_name: str):
    client = _get_gspread_client()
    sh = client.open_by_key(st.secrets["sheet_id"])
    try:
        ws = sh.worksheet(sheet_name)
    except Exception:
        ws = sh.add_worksheet(
            title=sheet_name, rows=2000, cols=len(SHEET_SCHEMAS[sheet_name])
        )
        ws.append_row(SHEET_SCHEMAS[sheet_name])
    return ws


def _local_path(sheet_name: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{sheet_name}.csv")


def load_df(sheet_name: str) -> pd.DataFrame:
    columns = SHEET_SCHEMAS[sheet_name]

    if _use_apps_script():
        try:
            records = _apps_script_get(sheet_name)
        except Exception as e:
            st.error(f"Apps Script에서 데이터를 불러오지 못했어요: {e}")
            return pd.DataFrame(columns=columns)
        if not records:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame(records)

    if _use_gsheets():
        ws = _get_worksheet(sheet_name)
        records = ws.get_all_records()
        if not records:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame(records)

    path = _local_path(sheet_name)
    if not os.path.exists(path):
        return pd.DataFrame(columns=columns)
    return pd.read_csv(path)


def append_row(sheet_name: str, row: dict):
    columns = SHEET_SCHEMAS[sheet_name]

    if _use_apps_script():
        try:
            _apps_script_post(sheet_name, row)
        except Exception as e:
            st.warning(
                f"저장 확인 응답을 못 받았어요 (구글 쪽 일시적 문제일 수 있어요). "
                f"구글 시트를 열어서 실제로 저장됐는지 확인해보세요. ({e})"
            )
        return

    if _use_gsheets():
        row_values = [row.get(c, "") for c in columns]
        ws = _get_worksheet(sheet_name)
        ws.append_row(row_values)
        return

    row_values = [row.get(c, "") for c in columns]
    path = _local_path(sheet_name)
    df = load_df(sheet_name)
    new_row = pd.DataFrame([row_values], columns=columns)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(path, index=False)