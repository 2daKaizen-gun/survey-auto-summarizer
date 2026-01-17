import pandas as pd
# import time
import os
from dotenv import load_dotenv  # 환경 변수 로드용
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build

# .env 파일에 저장된 환경 변수를 불러옵니다.
load_dotenv()

# 1. 설정 정보
SERVICE_ACCOUNT_FILE = 'credentials.json'
SPREADSHEET_ID = '1Ceks16DvtW0FduRUMnHxK6GYcx2EPXocZlz7KPawZMY' 
RANGE_NAME = '설문지 응답 시트1!A1:H' # 전체 행을 읽어오도록 설정

# Gemini API 설정
# 보안 강화: 코드가 아닌 환경 변수에서 키를 가져옵니다.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def get_sheets_service():
    """구글 시트 API 인증 및 서비스 생성"""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, 
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    return build('sheets', 'v4', credentials=creds)

# --- 종합 분석 함수 ---
def generate_batch_insight(df):
    """
    모든 응답 데이터를 분석하여 국적/성별/참석여부별 종합 리포트를 생성합니다.
    """
    model = genai.GenerativeModel('gemini-flash-latest')
    
    # 1. 데이터를 AI가 읽기 좋은 텍스트 리스트로 변환 (데이터 직렬화)
    data_context = ""
    for _, row in df.iterrows():
        data_context += f"- [정보: {row['국적']}/{row['성별']}/{row['마지막 행사 참석 여부']}] 내용: {row['느낀 점 (100자 이상)']}\n"

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
    response = model.generate_content(prompt)
    return response.text.strip()

def update_sheet_report(service, spreadsheet_id, report_text, last_row):
    """
    생성된 종합 리포트를 데이터 하단에 기록합니다.
    """
    # 데이터가 끝나는 행(last_row)보다 2칸 아래부터 기록 시작
    target_row = last_row + 3 
    target_range = f'설문지 응답 시트1!A{target_row}' 
    
    body = {
        'values': [
            ["AI 종합 인사이트 리포트"], # 제목 행 (A열)
            [report_text]              # 내용 행 (A열)
        ]
    }
    
    # 구글 시트에 데이터 쓰기 실행
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=target_range,
        valueInputOption="USER_ENTERED", # 줄바꿈(\n) 등을 시트에서 인식하도록 설정
        body=body
    ).execute()
    
    print(f"구글 시트 {target_range} 위치에 리포트 기록을 완료했습니다.")

def main():
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

        # [3] 데이터 현황 확인
        print(f"총 {len(df)}개의 데이터를 기반으로 종합 분석을 시작합니다...")

        # [4] 종합 인사이트 생성 (배치 처리)
        # 루프를 돌며 한 명씩 하는 게 아니라, df 전체를 함수에 던집니다.
        print("Gemini AI가 그룹별 패턴을 분석 중입니다. 잠시만 기다려주세요...")
        
        try:
            final_report = generate_batch_insight(df)
            print("-" * 50 + "\n" + final_report + "\n" + "-" * 50)
            
            # [5] 시트에 결과 기록 
            last_data_row = len(df) + 1 
            update_sheet_report(service, SPREADSHEET_ID, final_report, last_data_row)
            
        except Exception as ai_error:
            print(f"AI 분석/기록 에러: {ai_error}")

    except Exception as fatal_error:
        print(f"시스템 에러: {fatal_error}")

if __name__ == '__main__':
    main()