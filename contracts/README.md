# contracts/ — 단일 진실 공급원(SSOT)

FE/BE의 **유일한 결합점**. Pydantic 원본 → JSON Schema / TS 타입을 생성해 프론트가 소비한다.

## 현재 (Track 0)
계약의 뼈대는 백엔드 Pydantic으로 존재:
- 응답 봉투 · error-code: `backend/app/shared/schemas.py` (`ApiResponse`, `ErrorCode`)
- auth I/O: `backend/app/domains/auth/schemas.py`
- JWT 클레임: `{sub(user_id), role, org_id, type, iat, exp}`

## 생성 파이프라인 (예정)
```
Pydantic 모델 → JSON Schema(model_json_schema) → TS 타입(json-schema-to-typescript)
            → frontend/src/api/types.gen.ts
```
- 백엔드 dev 의존성: `datamodel-code-generator`(역방향) 또는 `model_json_schema()` 덤프 스크립트
- CI: 타입 재생성 후 `git diff --exit-code`로 **드리프트 0** 검증 (llms.txt CI/CD 참고)

> 규칙: 새 API/에이전트는 **여기 계약부터** 정의 → 그다음 구현. 트랙 간 결합은 계약으로만.
