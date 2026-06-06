"""ads 유스케이스 — multipart(이미지/텍스트) + Storage 포트."""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.agents.analyzer.agent import AnalyzerAgent
from app.ai.kernel.registry import registry
from app.contracts.simulation_pipeline import AdInput
from app.domains.ads.repository import AdRepository
from app.domains.ads.schemas import AdOut, CreateTextAdRequest
from app.domains.ads.validation import validate_image
from app.infra.storage import get_storage
from app.models.ad import Ad
from app.models.enums import AdInputType, AdStatus
from app.shared.exceptions import AppException
from app.shared.project_access import assert_project_member
from app.shared.schemas import ErrorCode


def _ensure_analyzer() -> None:
    if not registry.has("analyzer"):
        registry.register(AnalyzerAgent())


class AdService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = AdRepository(db)

    @staticmethod
    def _out(ad: Ad) -> AdOut:
        return AdOut(
            id=ad.id,
            project_id=ad.project_id,
            created_by=ad.created_by,
            name=ad.name,
            input_type=ad.input_type,
            text_content=ad.text_content,
            storage_url=ad.storage_url,
            analysis_status=ad.analysis_status,
            analysis_result=ad.analysis_result,
            analysis_confidence=ad.analysis_confidence,
            created_at=ad.created_at,
            updated_at=ad.updated_at,
        )

    async def list_for_project(self, project_id: uuid.UUID, user_id: str) -> list[AdOut]:
        await assert_project_member(self.db, project_id, uuid.UUID(user_id))
        ads = await self.repo.list_by_project(project_id)
        return [self._out(a) for a in ads]

    async def get_ad(self, ad_id: uuid.UUID, user_id: str) -> AdOut:
        ad = await self.repo.get(ad_id)
        if not ad:
            raise AppException(ErrorCode.NOT_FOUND, "광고를 찾을 수 없습니다", 404)
        await assert_project_member(self.db, ad.project_id, uuid.UUID(user_id))
        return self._out(ad)

    async def create_text(self, user_id: str, body: CreateTextAdRequest) -> AdOut:
        text_content = {"headline": body.headline, "body": body.body, "cta": body.cta}
        return await self._create_and_analyze(
            user_id=user_id,
            project_id=body.project_id,
            name=body.name,
            input_type=AdInputType.text,
            text_content=text_content,
        )

    async def create_multipart(
        self,
        user_id: str,
        project_id: uuid.UUID,
        name: str,
        input_type: str,
        *,
        headline: str | None = None,
        body: str | None = None,
        cta: str | None = None,
        file_bytes: bytes | None = None,
        file_content_type: str | None = None,
        file_filename: str | None = None,
    ) -> AdOut:
        if input_type == "text":
            if not all([headline, body, cta]):
                raise AppException(
                    ErrorCode.VALIDATION_ERROR,
                    "텍스트 광고는 headline, body, cta가 필요합니다",
                    400,
                )
            return await self._create_and_analyze(
                user_id=user_id,
                project_id=project_id,
                name=name,
                input_type=AdInputType.text,
                text_content={"headline": headline, "body": body, "cta": cta},
            )

        if input_type == "image":
            if not file_bytes:
                raise AppException(ErrorCode.VALIDATION_ERROR, "이미지 파일이 필요합니다", 400)
            ext = validate_image(file_content_type, len(file_bytes))
            ad_id = uuid.uuid4()
            key = f"ads/{project_id}/{ad_id}{ext}"
            stored = await get_storage().upload(key, file_bytes, file_content_type or "image/jpeg")
            return await self._create_and_analyze(
                user_id=user_id,
                project_id=project_id,
                name=name,
                input_type=AdInputType.image,
                storage_path=stored.path,
                storage_url=stored.url,
                ad_id=ad_id,
            )

        raise AppException(
            ErrorCode.VALIDATION_ERROR,
            "input_type은 text 또는 image 여야 합니다",
            400,
        )

    async def _create_and_analyze(
        self,
        user_id: str,
        project_id: uuid.UUID,
        name: str,
        input_type: AdInputType,
        *,
        text_content: dict | None = None,
        storage_path: str | None = None,
        storage_url: str | None = None,
        ad_id: uuid.UUID | None = None,
    ) -> AdOut:
        await assert_project_member(self.db, project_id, uuid.UUID(user_id))
        ad = Ad(
            id=ad_id or uuid.uuid4(),
            project_id=project_id,
            created_by=uuid.UUID(user_id),
            name=name,
            input_type=input_type,
            text_content=text_content,
            storage_path=storage_path,
            storage_url=storage_url,
            analysis_status=AdStatus.analyzing,
        )
        self.repo.add(ad)
        await self.db.flush()

        _ensure_analyzer()
        result = await registry.get("analyzer").run(
            {
                "ad": AdInput(
                    ad_id=ad.id,
                    input_type=input_type,
                    name=name,
                    text_content=text_content,
                    image_url=storage_url,
                ).model_dump(mode="json")
            }
        )
        ad.analysis_result = result.output
        ad.analysis_confidence = 0.85
        ad.analysis_status = AdStatus.completed
        await self.db.commit()
        await self.db.refresh(ad)
        return self._out(ad)
