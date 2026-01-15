import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 1. 설정 정보 (본인의 환경에 맞게 수정 필요!)
SERVICE_ACCOUNT_FILE = 'credentials.json'
# 구글 시트 주소창에서 ID를 복사해서 아래에 붙여넣으세요!
SPREADSHEET_ID = '1Ceks16DvtW0FduRUMnHxK6GYcx2EPXocZlz7KPawZMY' 
RANGE_NAME = '설문지 응답 시트1!A1:G2' # 시트이름!범위

def get_sheets_service():
    """구글 시트 API 서비스 객체 생성"""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, 
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )
    service = build('sheets', 'v4', credentials=creds)
    return service

def main():
    service = get_sheets_service()
    sheet = service.spreadsheets()
    
    # 데이터 가져오기 호출
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('데이터를 찾을 수 없습니다.')
    else:
        print('✅ 연결 성공! 데이터를 가져왔습니다:')
        for row in values:
            print(row)

if __name__ == '__main__':
    main()