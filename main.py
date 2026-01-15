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
        print("처리할 데이터가 없습니다.")
        return

    # [2] 데이터 정규화 (Data Normalization)
    # 구글 시트의 빈 셀 때문에 발생하는 컬럼 수 불일치 해결
    headers = values[0]
    raw_data = values[1:]
    
    # 각 행을 돌며 헤더 길이보다 짧으면 빈 칸('')으로 채움 (List Comprehension)
    normalized_data = [row + [''] * (len(headers) - len(row)) for row in raw_data]

    # [3] Pandas DataFrame 생성
    df = pd.DataFrame(normalized_data, columns=headers)

    # [4] 요약 대상 필터링 (AI 요약 결과가 비어있는 행만 추출)
    output_column = 'AI 요약 결과(Output)'
    target_column = '느낀 점(100자 이상)'

    # 'AI 요약 결과'가 비어 있는 행만 골라냅니다 (새로 들어온 데이터)
    new_data_mask = df[output_column].str.strip() == ''
    new_df = df[new_data_mask]

    print(f"전체 응답: {len(df)}개 | 요약이 필요한 신규 응답: {len(new_df)}개")

    # [5] 반복문을 돌며 개별 데이터 매핑
    if not new_df.empty:
        for index, row in new_df.iterrows():
            #중요: 실제 구글 시트의 행 번호 (Pandas 인덱스 + 헤더(1) + 1 = index + 2)
            sheet_row_num = index + 2 
            
            feedback = row[target_column].strip()
            
            if feedback:
                print(f"[시트 {sheet_row_num}행] 처리 대기: {row['성함을 알려주세요.']} 님")
                # (여기에 나중에 Phase 3의 AI 요약 함수를 호출할 예정입니다)
            else:
                print(f"[시트 {sheet_row_num}행] 내용이 없어 건너뜁니다.")
    else:
        print("모든 데이터가 이미 요약되어 처리할 내용이 없습니다.")

if __name__ == '__main__':
    main()