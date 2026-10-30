import pandas as pd
import os
import time
from datetime import datetime
from dotenv import load_dotenv  # 환경 변수 로드용
from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pydantic import BaseModel

# .env 파일에 저장된 환경 변수를 불러옵니다.
load_dotenv()

# 1. 설정 정보 (환경 변수 우선, 없으면 기본값 사용)
# (빈 문자열로 설정된 경우에도 기본값을 쓰도록 `or` 사용)
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE") or 'credentials.json'
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME") or '설문지 응답 시트1'
RANGE_NAME = f'{SHEET_NAME}!A1:H' # 전체 행을 읽어오도록 설정
# 리포트는 응답 시트와 분리된 탭에 기록 (재실행 시 응답 데이터와 섞이지 않도록)
REPORT_SHEET_NAME = os.getenv("REPORT_SHEET_NAME") or 'AI 리포트'

# 분석에 필요한 설문 컬럼
FEEDBACK_COLUMN = '느낀 점 (100자 이상)'
REQUIRED_COLUMNS = ['국적', '성별', '마지막 행사 참석 여부', FEEDBACK_COLUMN]
# 응답별 한 줄 요약을 기록할 컬럼 (시트에 없으면 개별 요약은 건너뜀)
SUMMARY_COLUMN = 'AI요약 결과'

# Gemini API 설정
# 보안 강화: 코드가 아닌 환경 변수에서 키를 가져옵니다.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL") or 'gemini-flash-latest'
# 할당량 초과(429)·일시적 서버 오류(503) 시 재시도 설정
MAX_RETRIES = 3
RETRY_BASE_SECONDS = 10
RETRYABLE_STATUS_CODES = (429, 503)

def validate_config():
    """실행 전 필수 설정이 준비되었는지 확인합니다."""
    errors = []
    if not GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
    if not SPREADSHEET_ID:
        errors.append("SPREADSHEET_ID가 설정되지 않았습니다. .env 파일에 시트 URL의 /d/ 와 /edit 사이 값을 넣으세요.")
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        errors.append(f"서비스 계정 키 파일({SERVICE_ACCOUNT_FILE})을 찾을 수 없습니다.")
    for message in errors:
        print(f"설정 오류: {message}")
    return not errors

def get_sheets_service():
    """구글 시트 API 인증 및 서비스 생성"""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, 
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    return build('sheets', 'v4', credentials=creds)

def call_gemini(prompt, config=None):
    """Gemini를 호출합니다. 일시적 오류는 대기 시간을 늘려가며 재시도합니다."""
    client = genai.Client(api_key=GEMINI_API_KEY)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt, config=config)
            break
        except genai_errors.APIError as e:
            if e.code not in RETRYABLE_STATUS_CODES or attempt == MAX_RETRIES:
                raise
            wait = RETRY_BASE_SECONDS * 2 ** (attempt - 1)
            print(f"Gemini API 일시 오류({e.code}). {wait}초 후 재시도합니다... ({attempt}/{MAX_RETRIES - 1})")
            time.sleep(wait)

    # 안전 정책 차단 등으로 본문 없이 응답이 오는 경우 원인을 안내
    if not response.text:
        block_reason = getattr(response.prompt_feedback, 'block_reason', None)
        finish_reason = response.candidates[0].finish_reason if response.candidates else None
        raise ValueError(
            f"Gemini가 빈 응답을 반환했습니다 (차단 사유: {block_reason}, 종료 사유: {finish_reason}). "
            "응답 데이터나 프롬프트에 정책 위반 소지가 있는지 확인하세요."
        )
    return response

# --- 응답별 한 줄 요약 함수 ---
class RowSummary(BaseModel):
    id: int       # 시트 행 번호
    summary: str  # 한 줄 요약

def generate_row_summaries(df):
    """
    각 응답의 소감을 한 줄로 요약합니다. API 호출은 한 번으로 묶어 처리합니다.
    반환값: {시트 행 번호: 요약}
    """
    # 개인 식별 정보 없이 행 번호와 소감만 전달
    data_context = "".join(f"[{row_number}] {row[FEEDBACK_COLUMN]}\n" for row_number, row in df.iterrows())

    prompt = f"""
    너는 대학 행사 설문 응답을 정리하는 조교야. 아래 각 응답을 핵심만 담아 한 줄로 요약해줘.

    [응답 목록] (대괄호 안 숫자가 id)
    {data_context}

    [출력 규칙]
    - 모든 id에 대해 빠짐없이 하나씩 요약할 것.
    - 요약은 40자 내외의 한국어 한 문장으로, 만족/불만 포인트가 드러나게 작성할 것.
    - 응답이 외국어여도 요약은 한국어로 작성할 것.
    """

    config = genai_types.GenerateContentConfig(
        response_mime_type='application/json',
        response_schema=list[RowSummary],
    )
    response = call_gemini(prompt, config)
    summaries = {item.id: item.summary.strip() for item in (response.parsed or [])}
    # 요청하지 않은 id는 무시 (다른 행을 덮어쓰지 않도록)
    return {row_number: summaries[row_number] for row_number in df.index if summaries.get(row_number)}

def update_row_summaries(service, spreadsheet_id, summaries, column_letter):
    """한 줄 요약을 각 응답 행의 요약 컬럼에 기록합니다."""
    data = [
        {'range': f"'{SHEET_NAME}'!{column_letter}{row_number}", 'values': [[summary]]}
        for row_number, summary in summaries.items()
    ]
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'valueInputOption': 'RAW', 'data': data}
    ).execute()
    print(f"{len(data)}개 응답의 한 줄 요약을 '{SUMMARY_COLUMN}' 컬럼에 기록했습니다.")

# --- 종합 분석 함수 ---
def generate_batch_insight(df):
    """
    모든 응답 데이터를 분석하여 국적/성별/참석여부별 종합 리포트를 생성합니다.
    """
    # 1. 데이터를 AI가 읽기 좋은 텍스트 리스트로 변환 (데이터 직렬화)
    data_context = ""
    for _, row in df.iterrows():
        data_context += f"- [정보: {row['국적']}/{row['성별']}/{row['마지막 행사 참석 여부']}] 내용: {row[FEEDBACK_COLUMN]}\n"

    # 2. 기획안을 반영한 정교한 프롬프트 (Phase 3-1 설계 반영)
    prompt = f"""
    너는 대학 행사 설문 분석 전문가야. 아래 제공된 [학생 응답 데이터] 전체를 읽고 종합 분석 보고서를 작성해줘.

    [학생 응답 데이터]
    {data_context}

    [분석 요청 사항]
    1. 참석 여부에 따라 만족도나 활동의 유익함에 어떤 차이가 있는지 분석할 것.
    2. 국적별(특히 한국, 일본, 중국 등)로 언어 장벽이나 활동 이해도에 어떤 차이가 있는지 비교할 것.
    3. 성별에 따라 활동 참여 방식이나 적극성에 어떤 특징이 관찰되는지 도출할 것.

    [출력 규칙]
    - 전체 트렌드를 아우르는 유기적인 한 문단으로 작성할 것.
    - 정중한 한국어 문체를 사용할 것.
    - "분석 결과입니다" 같은 군더더기 없이 본론만 바로 시작할 것.
    """
    
    # AI 호출
    return call_gemini(prompt).text.strip()

def ensure_report_sheet(service, spreadsheet_id):
    """리포트 탭이 없으면 새로 만듭니다."""
    meta = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id, fields='sheets.properties.title'
    ).execute()
    titles = [s['properties']['title'] for s in meta.get('sheets', [])]
    if REPORT_SHEET_NAME not in titles:
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': [{'addSheet': {'properties': {'title': REPORT_SHEET_NAME}}}]}
        ).execute()
        print(f"'{REPORT_SHEET_NAME}' 탭을 새로 만들었습니다.")

def update_sheet_report(service, spreadsheet_id, report_text, response_count):
    """
    생성된 종합 리포트를 리포트 전용 탭에 기록합니다. (이전 리포트는 덮어씀)
    """
    ensure_report_sheet(service, spreadsheet_id)
    target_range = f"'{REPORT_SHEET_NAME}'!A1"

    body = {
        'values': [
            ["AI 종합 인사이트 리포트"],                                    # 제목 행
            ["생성 시각", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ["분석 응답 수", response_count],
            [report_text]                                                   # 내용 행
        ]
    }

    # 이전 리포트를 지운 뒤 새로 기록
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id, range=f"'{REPORT_SHEET_NAME}'", body={}
    ).execute()
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=target_range,
        valueInputOption="RAW", # AI 출력이 '='로 시작해도 수식으로 해석되지 않도록 원문 그대로 기록
        body=body
    ).execute()

    print(f"구글 시트 '{REPORT_SHEET_NAME}' 탭에 리포트 기록을 완료했습니다.")

def main():
    if not validate_config():
        return

    # [1] 데이터 로드
    try:
        service = get_sheets_service()
        sheet = service.spreadsheets()
        try:
            result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        except Exception as e:
            print(f"구글 시트 로드 중 에러 발생: {e}")
            return
        
        values = result.get('values', [])
        if not values:
            print("처리할 데이터가 없습니다.")
            return

        # [2] 데이터 정규화 (Data Normalization)
        # 구글 시트의 빈 셀 때문에 발생하는 컬럼 수 불일치 해결
        headers = values[0]
        raw_data = values[1:]
        # 각 행을 돌며 헤더 길이보다 짧으면 빈 칸('')으로 채움 (List Comprehension)
        normalized_data = [row + [''] * (len(headers) - len(row)) for row in raw_data]
        # Pandas DataFrame 생성
        df = pd.DataFrame(normalized_data, columns=headers)
        # 인덱스를 실제 시트 행 번호로 맞춤 (헤더가 1행이므로 데이터는 2행부터)
        df.index = range(2, len(df) + 2)

        missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            print(f"시트에 필요한 컬럼이 없습니다: {', '.join(missing)}")
            return

        # 소감이 비어 있는 행(빈 행, 이전 버전이 시트 하단에 남긴 리포트 행 등)은 분석에서 제외
        df = df[df[FEEDBACK_COLUMN].str.strip() != '']
        if df.empty:
            print("분석할 응답이 없습니다.")
            return

        # [3] 응답별 한 줄 요약 (요약 컬럼이 비어 있는 응답만 처리)
        if SUMMARY_COLUMN in df.columns:
            pending = df[df[SUMMARY_COLUMN].str.strip() == '']
            if pending.empty:
                print("모든 응답에 이미 한 줄 요약이 있습니다.")
            else:
                print(f"{len(pending)}개 응답의 한 줄 요약을 생성합니다...")
                try:
                    summaries = generate_row_summaries(pending)
                    column_letter = chr(ord('A') + headers.index(SUMMARY_COLUMN))
                    update_row_summaries(service, SPREADSHEET_ID, summaries, column_letter)
                    if len(summaries) < len(pending):
                        print(f"{len(pending) - len(summaries)}개 응답은 요약이 누락되어 다음 실행 때 다시 시도합니다.")
                except Exception as summary_error:
                    # 개별 요약 실패가 종합 리포트 생성을 막지 않도록 분리
                    print(f"한 줄 요약 에러: {summary_error}")
        else:
            print(f"'{SUMMARY_COLUMN}' 컬럼이 없어 응답별 요약은 건너뜁니다.")

        # [4] 데이터 현황 확인
        print(f"총 {len(df)}개의 데이터를 기반으로 종합 분석을 시작합니다...")

        # [5] 종합 인사이트 생성 (배치 처리)
        # 루프를 돌며 한 명씩 하는 게 아니라, df 전체를 함수에 던집니다.
        print("Gemini AI가 그룹별 패턴을 분석 중입니다. 잠시만 기다려주세요...")
        
        try:
            final_report = generate_batch_insight(df)
            print("-" * 50 + "\n" + final_report + "\n" + "-" * 50)
            
            # [6] 시트에 결과 기록
            update_sheet_report(service, SPREADSHEET_ID, final_report, len(df))
            
        except Exception as ai_error:
            print(f"AI 분석/기록 에러: {ai_error}")

    except Exception as fatal_error:
        print(f"시스템 에러: {fatal_error}")

if __name__ == '__main__':
    main()