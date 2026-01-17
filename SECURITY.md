# 🛡️ Security Policy

이 프로젝트는 사용자 데이터 및 API 인증 정보의 안전한 관리를 중요시 합니다.

## 1. Secret Management (인증 정보 관리)
- **Environment Variables**: Gemini API 및 Google Sheets API 인증을 위한 키는 코드에 직접 노출하지 않고 `.env` 파일을 통해 관리합니다.
- **Git Ignore**: `.env` 파일과 `credentials.json` 등 민감한 파일은 `.gitignore`에 등록하여 원격 저장소(GitHub)에 업로드되지 않도록 철저히 차단합니다.

## 2. Security Incident Response (보안 사고 대응)
만약 API 키가 외부에 노출되는 사고가 발생할 경우, 즉시 대응합니다:
1. **Key Rotation**: 노출된 API 키를 Google Cloud Console / AI Studio에서 즉시 삭제 및 무효화합니다.
2. **New Key Issuance**: 새로운 키를 발급받아 로컬 환경 변수를 업데이트합니다.
3. **Commit History Cleanup**: `git push --force` 등을 사용하여 노출된 기록이 포함된 이전 커밋을 제거하거나 덮어씁니다.

## 3. Vulnerability Reporting (취약점 보고)
프로젝트 내에서 보안 취약점을 발견하신 경우, 이슈(Issue)를 생성하거나 아래 연락처로 연락해 주시면 감사하겠습니다.

- **Email**: hkys1223@naver.com