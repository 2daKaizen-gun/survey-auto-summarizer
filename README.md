# 📋 survey-auto-summarizer

구글 폼 응답 자동 분석(analyze) 및 요약 도구입니다.

## 📊 Planning and building
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

##  🛠️ Technology Stack
- **Language**: Python 3.14.0
- **Libraries**: Pandas, google-api-python-client, google-auth-oauthlib, python-dotenv
- **AI Engine**: Google gemini-flash-latest

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
  - [ ] Phase 3-3: Automatic recording of results
  - [ ] Phase 3-4: Create Final README
