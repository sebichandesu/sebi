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


def _apps_script_get(sheet_name: str):
    url = st.secrets["apps_script_url"]
    key = st.secrets["apps_script_key"]
    res = requests.get(url, params={"sheet": sheet_name, "key": key}, timeout=10)
    res.raise_for_status()
    return res.json()


def _apps_script_post(sheet_name: str, row: dict):
    url = st.secrets["apps_script_url"]
    key = st.secrets["apps_script_key"]
    payload = {"sheet": sheet_name, "key": key, "row": row}
    res = requests.post(url, json=payload, timeout=10)
    res.raise_for_status()
    return res.json()


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
        _apps_script_post(sheet_name, row)
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