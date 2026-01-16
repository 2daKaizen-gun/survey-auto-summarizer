# 📋 survey-auto-summarizer

구글 폼 응답 자동 요약 도구입니다.

## 📊 Planning and building
- **데이터 소스**: 구글 폼 (행사 참석 여부 및 활동 마무리 후기)
- **주요 컬럼**:
  1. 타임스탬프
  2. 참석여부 (객관식)
  3. 성함
  4. 국적 (객관식)
  5. 학번
  6. **느낀점 100자 이상** (AI 분석 대상)
  7. **AI요약 결과** (결과 기록 열)

##  🛠️ Technology Stack
- **Language**: Python 3.14.0
- **Libraries**: Pandas, google-api-python-client, google-auth-oauthlib, python-dotenv
- **AI Engine**: Google Gemini 1.5 Flash (예정)

## ✅ Milestone
- Phase 1: Planning and building a Google cloud environment
  - [v] Phase 1-1: Determining Project Scope
  - [v] Phase 1-2: Google Cloud Console
  - [v] Phase 1-3: Create Service Account & credentials.json
  - [v] Phase 1-4: Configuring the Development Environment (.gitignore, venv)
  - [v] Phase 1-5: Confirmation of technology stack (requirements.txt)

- Phase 2: Implementing Google Sheet Data Pipeline
  - [v] Phase 2-1: API Interworking Test (Data Load)
  - [v] Phase 2-2: Pandas preprocessing logic (Data Normalization & Padding)
  - [v] Phase 2-3: Real-time data response (Filtering unprocessed rows)
  - [v] Phase 2-4: Error Handling (Try-Except, time.sleep)

- Phase 3: AI Summary Engine and Results Feedback(Next)
  - [ ] Phase 3-1: Prompt Engineering
  - [ ] Phase 3-2: Interworking with AI API
  - [ ] Phase 3-3: Automatic recording of results
  - [ ] Phase 3-4: Create Final README