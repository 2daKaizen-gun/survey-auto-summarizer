# 📋 survey-auto-summarizer

An AI-powered insight pipeline that automates Google Forms data analysis and reporting using Gemini AI and Google Sheets API.

## 🎯 Background & Motivation
- The Context
  Following a large-scale International Exchange Program at the university, an extensive satisfaction survey was conducted. Due to the diverse background of the participants, the survey collected a vast amount of subjective feedback in multiple languages.

- The Problem
  Data Overload: Manually reading and summarizing hundreds of student reviews (minimum 100 characters each) required immense time and energy.

  Analysis Complexity: It was difficult for    humans to cross-analyze patterns based on nationality, gender, and participation status to find meaningful insights.

  Data Abandonment: Valuable feedback often remained scattered in spreadsheets, making it difficult to utilize as "lessons learned" for future program planning.

- The Solution
  Automated Pipeline: Built a system that loads real-time data from Google Sheets for immediate processing.

  AI Cross-Analysis: Leveraged Gemini AI to analyze cultural differences (e.g., language barriers for specific nationalities) and participation trends.

  Automated Feedback: Analysis reports are automatically written back to the source spreadsheet for stakeholder review.

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

- **Data Handling**: Pandas(Normalization & Padding)

- **API Integration**: Google Sheets API v4

- **AI Engine**: Google Gemini 2.0 Flash (gemini-flash-latest)

- **Security**: python-dotenv, .gitignore (Environment Variable Management)

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

## 🔥 Troubleshooting & Lessons Learned
1. AI Model & Quota Management (404 & 429 Errors)
Challenge: Encountered 404 errors due to deprecated model identifiers and 429 errors from free-tier quota limits.

Resolution: Debugged using genai.list_models() to identify stable identifiers and switched to gemini-flash-latest. Optimized API consumption by implementing batch processing instead of individual row calls.

2. Security Incident Response (Secret Management)
Challenge: Exposed API keys detected by GitHub Secret Scanning.

Resolution: Immediately revoked and rotated the exposed keys. Implemented a secure environment variable system using .env and cleaned git history to prevent future leaks.

3. Data Normalization & Consistency
Challenge: Inconsistent column counts due to empty cells in Google Sheets caused DataFrame construction errors.

Resolution: Implemented a data padding logic to ensure structural consistency across all input rows.

## 🧐 Self-Reflection
Technical Growth
System Integration: Gained hands-on experience in architecting a data pipeline that bridges Google Workspace and Generative AI services.

Security Mindset: Developed a professional habit of "Security First" by managing sensitive credentials through environment variables.

Problem-Solving Mindset
User-Centric Development: Realized that developers are not just "coders" but "problem solvers" who bridge the gap between human inconvenience and technical solutions.

Future Roadmap
UI/UX Improvement: Plan to build a web interface using Streamlit or Flask for non-technical administrators.

Real-time Triggers: Integrating Google Apps Script (GAS) for true real-time automation triggered by form submissions.

## 📈 Results
- **Efficiency**: Reduced survey analysis and summary time by over 95% compared to manual labor.
- **Accuracy**: Successfully extracted nuanced insights based on nationality and gender, providing a data-driven foundation for future program planning.

## ✨ Connect with Me
- **GitHub Repository**: https://github.com/2daKaizen-gun/survey-auto-summarizer