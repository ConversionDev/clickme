# contracts/ — 단일 진실 공급원(SSOT)

FE/BE의 **유일한 결합점**. Pydantic 원본 → JSON Schema / TS 타입을 생성해 프론트가 소비한다.

## 현재 (Track 0+)
Pydantic SSOT → JSON Schema export:
- 공통: `backend/app/shared/schemas.py` (`ApiResponse`, `ErrorCode`)
- auth: `backend/app/domains/auth/schemas.py`
- simulation·SSE: `backend/app/contracts/`

## 생성 파이프라인
```bash
cd backend
uv run python -m scripts.export_contracts
```
→ `contracts/*.schema.json` 갱신 (FE `types.gen.ts` 생성은 후속)

JWT 클레임: `{sub(user_id), role, org_id, type, iat, exp}`

> 규칙: 새 API/에이전트는 **여기 계약부터** 정의 → 그다음 구현. 트랙 간 결합은 계약으로만.
