import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 1. 설정 정보
SERVICE_ACCOUNT_FILE = 'credentials.json'
SPREADSHEET_ID = '1Ceks16DvtW0FduRUMnHxK6GYcx2EPXocZlz7KPawZMY' 
RANGE_NAME = '설문지 응답 시트1!A1:G' # 전체 행을 읽어오도록 설정

def get_sheets_service():
    """구글 시트 API 인증 및 서비스 생성"""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, 
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )
    return build('sheets', 'v4', credentials=creds)

def main():
    # [1] 데이터 로드
    service = get_sheets_service()
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print("❌ 처리할 데이터가 없습니다.")
        return

    # [2] 데이터 정규화 (Data Normalization)
    # 구글 시트의 빈 셀 때문에 발생하는 컬럼 수 불일치 해결
    headers = values[0]
    raw_data = values[1:]
    
    # 각 행을 돌며 헤더 길이보다 짧으면 빈 칸('')으로 채움 (List Comprehension)
    normalized_data = [row + [''] * (len(headers) - len(row)) for row in raw_data]

    # [3] Pandas DataFrame 생성
    df = pd.DataFrame(normalized_data, columns=headers)

    # [4] 데이터 정제 및 추출 (Cleaning)
    # AI가 요약할 대상인 '느낀 점' 컬럼만 추출 (결측치 제거)
    target_column = '느낀 점(100자 이상)'
    
    if target_column in df.columns:
        # 내용이 비어있지 않은 데이터만 필터링(.str.strip() != '')
        feedback_series = df[df[target_column].str.strip() != ''][target_column]
        
        print(f"✅ 총 {len(feedback_series)}개의 유효한 응답을 확인했습니다.")
        
        # 실제 데이터 상위 3개만 깔끔하게 확인
        for i, text in enumerate(feedback_series.head(3)):
            print(f"[{i+1}] {text[:50]}...")
    else:
        print(f"❌ '{target_column}' 컬럼을 찾을 수 없습니다.")

if __name__ == '__main__':
    main()