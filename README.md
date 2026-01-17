# 📋 survey-auto-summarizer

구글 폼 응답 자동 분석(analysis) 및 요약 도구입니다.

## 📊 Planning and building
- 본 프로젝트는 대학교 내 국제 프로그램 행사 후 얻은 대량의 설문 데이터를 수작업으로 요약, 정리 및 분석하는 번거로움을 해결하기 위해 기획되었습니다.

- **데이터 소스**: 구글 폼 (행사 참석 여부 및 활동 마무리 후기)

- **주요 컬럼**:
  1. 타임스탬프
  2. 마지막 행사 참석 여부
  3. 성함
  4. 성별
  5. 국적
  6. 학번
  7. **느낀점 (100자 이상)**
  8. **AI분석 결과** (Aggregate Insights)

- 단순 요약을 넘어 국적, 성별, 행사 참석 여부에 따른 통계적 인사이트를 AI가 직접 도출, 시트에 재 기록하여 End-to-End 자동화 파이프라인을 구축했습니다.

##  🛠️ Technology Stack
- **Language**: Python 3.14.0

- **Libraries**: 
  - Pandas: 데이터 정규화 및 전처리를 위한 데이터 프레임 핸들링
  - google-api-python-client: Google Sheets API 연동 및 데이터 Read/Write
  - google-generativeai: Gemini AI 모델 연동 및 프롬프트 제어
  - python-dotenv: API Key 등 민감 정보의 환경 변수 관리

- **AI Engine**: Google Gemini 2.0 Flash (stable)

- **Security**: 환경 변수 기반 인증 관리

## ✅ Milestone
- Phase 1: Planning and building a Google cloud environment
  - [x] Phase 1-1: Determining Project Scope
  - [x] Phase 1-2: Google Cloud Console
  - [x] Phase 1-3: Create Service Account & credentials.json
  - [x] Phase 1-4: Configuring the Development Environment (.gitignore, venv)
  - [x] Phase 1-5: Confirmation of technology stack (requirements.txt)

- Phase 2: Implementing Google Sheet Data Pipeline
  - [x] Phase 2-1: API Interworking Test (Data Load)
  - [x] Phase 2-2: Pandas preprocessing logic (Data Normalization & Padding)
  - [x] Phase 2-3: Real-time data response (Filtering unprocessed rows)
  - [x] Phase 2-4: Error Handling (Try-Except, time.sleep)

- Phase 3: AI Summary Engine and Results Feedback(Next)
  - [x] Phase 3-1: Prompt Engineering
  - [x] Phase 3-2: Interworking with AI API
  - [x] Phase 3-3: Automatic recording of results
  - [x] Phase 3-4: Create Final README

## 💡 Troubleshooting & Lessons Learned (핵심 역량)
- **API 버전 및 모델 명세 관리**: gemini-1.5-flash 모델 호출 시 발생한 404 에러를 통해 API 버전별 모델 식별자(Identifier) 차이를 학습하고, gemini-flash-latest를 사용하여 안정성을 확보했습니다.

- **보안 사고 대응 및 Secret Management**: GitHub Secret Scanning을 통해 노출된 API Key를 즉시 무효화(Revoke)하고, .env 파일을 통한 환경 변수 관리 시스템을 도입하여 보안성을 강화했습니다.

- **데이터 배치 처리(Batch Processing) 최적화**: API 호출 횟수 제한(Quota)을 극복하기 위해 루프 기반 호출 방식에서 전체 데이터를 하나의 컨텍스트로 묶어 처리하는 방식으로 로직을 개선하여 효율성을 80% 이상 높였습니다.
