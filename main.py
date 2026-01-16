import pandas as pd
import time
import socket
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
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    return build('sheets', 'v4', credentials=creds)

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

        # [3] 신규 데이터 필터링 로직
        new_data_mask = df['AI 요약 결과(Output)'].str.strip() == ''
        new_df = df[new_data_mask]

        if new_df.empty:
            print("모든 데이터가 이미 처리되었습니다.")
            return
        print(f"총 {len(new_df)}개의 데이터 처리 시작")
        for index, row in new_df.iterrows():
            try:
                #실제 구글 시트의 행 번호 (Pandas 인덱스 + 헤더(1) + 1 = index + 2)
                sheet_row_num = index + 2 
                feedback = row['느낀 점(100자 이상)'].strip()
                
                if not feedback:
                    print(f"[{sheet_row_num}행] 내용 없음 - 스킵")
                    continue
                    # (여기에 나중에 Phase 3의 AI 요약 함수)

                print(f"[{sheet_row_num}행] {row['성함을 알려주세요.']}님 데이터 처리 중...")
            
                # [4] API 할당량 관리 (Rate Limiting)
                # 너무 빠르게 요청하면 구글이 차단할 수 있으므로 1초씩 쉬어줍니다.
                time.sleep(1) 
                
                # ------------------------------------------
            except Exception as row_error:
                print(f"[{sheet_row_num}행] 처리 중 에러 발생: {row_error}")
                continue # 한 행이 에러 나도 멈추지 않고 다음 행으로 진행
    
    except KeyboardInterrupt:
        print("\n 사용자에 의해 프로그램 중단됨.")
    except Exception as fatal_error:
        print(f"치명적 에러 발생: {fatal_error}")

if __name__ == '__main__':
    main()