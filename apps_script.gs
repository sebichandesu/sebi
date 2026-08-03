/**
 * 나만의 기록장 - 구글 시트 연동용 Apps Script
 *
 * 사용법 (PC든 모바일 브라우저든 동일하게 동작합니다):
 * 1. script.new 또는 script.google.com/create 접속 -> 새 Apps Script 프로젝트가 바로 생성됩니다.
 *    (구글 시트의 "확장 프로그램" 메뉴를 거칠 필요 없음 - 모바일에서 그 메뉴가 안 보여도 상관없어요)
 * 2. 기존 코드를 전부 지우고 이 파일 내용을 통째로 붙여넣기
 * 3. 아래 SHEET_ID 값에 내 구글 시트의 ID를 넣기
 *    (시트 주소 https://docs.google.com/spreadsheets/d/[여기부분]/edit 에서 복사)
 * 4. 아래 SECRET_KEY 값을 원하는 비밀번호로 바꾸기 (영어/숫자 조합 추천)
 * 5. 배포 > 새 배포 > 유형: 웹앱 > 실행: 나(Me) / 액세스 권한: 전체 공개(Anyone)
 * 6. 배포 후 나오는 웹앱 URL을 복사해서 Streamlit secrets.toml 의 apps_script_url 에 붙여넣기
 * 7. SECRET_KEY와 동일한 값을 secrets.toml 의 apps_script_key 에 넣기
 */

const SHEET_ID = "여기에_구글시트_ID_붙여넣기"; // 시트 주소창 URL 중간의 긴 문자열
const SECRET_KEY = "여기에_원하는_비밀번호_입력"; // 예: "my-secret-2024" 처럼 아무 문자열

const SCHEMAS = {
  Outfits: ["날짜", "옷차림", "메모"],
  Media: ["날짜", "종류", "제목", "별점", "감상평"],
  Expenses: ["날짜", "카테고리", "금액", "메모"],
  Habits: ["날짜", "습관", "완료"]
};

function _getSpreadsheet() {
  // SHEET_ID가 채워져 있으면 그 시트를 열고, 비어 있으면(예전 방식) 현재 연결된 시트를 사용
  if (SHEET_ID && SHEET_ID.indexOf("여기에") === -1) {
    return SpreadsheetApp.openById(SHEET_ID);
  }
  return SpreadsheetApp.getActiveSpreadsheet();
}

function _getSheet(name) {
  const ss = _getSpreadsheet();
  let sheet = ss.getSheetByName(name);
  if (!sheet) {
    sheet = ss.insertSheet(name);
    sheet.appendRow(SCHEMAS[name]);
  }
  return sheet;
}

function _json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

// 기록 불러오기: GET ?sheet=Outfits&key=비밀번호
function doGet(e) {
  if (!e.parameter.key || e.parameter.key !== SECRET_KEY) {
    return _json({ error: "unauthorized" });
  }
  const name = e.parameter.sheet;
  if (!SCHEMAS[name]) {
    return _json({ error: "unknown sheet: " + name });
  }
  const sheet = _getSheet(name);
  const values = sheet.getDataRange().getValues();
  if (values.length < 2) {
    return _json([]);
  }
  const headers = values[0];
  const rows = values.slice(1).map(function (row) {
    const obj = {};
    headers.forEach(function (h, i) {
      obj[h] = row[i];
    });
    return obj;
  });
  return _json(rows);
}

// 기록 추가하기: POST { sheet, key, row: {...} }
function doPost(e) {
  let body;
  try {
    body = JSON.parse(e.postData.contents);
  } catch (err) {
    return _json({ error: "invalid json" });
  }
  if (!body.key || body.key !== SECRET_KEY) {
    return _json({ error: "unauthorized" });
  }
  const name = body.sheet;
  if (!SCHEMAS[name]) {
    return _json({ error: "unknown sheet: " + name });
  }
  const sheet = _getSheet(name);
  const headers = SCHEMAS[name];
  const row = body.row || {};
  const values = headers.map(function (h) {
    return row[h] !== undefined ? row[h] : "";
  });
  sheet.appendRow(values);
  return _json({ ok: true });
}
