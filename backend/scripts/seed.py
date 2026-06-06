"""개발 seed — 05_seed_data.sql 전체 이식 (계정·페르소나·프로젝트·광고·샘플 시뮬/리포트/채팅).
마이그레이션 후 실행: `uv run python -m scripts.seed` (멱등 — admin 존재 시 스킵)
비밀번호: admin@clickme.io = ChangeMe123! / 나머지 = Password123!  (배포 시 변경)"""
import asyncio
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.models import (
    Ad,
    ChatMessage,
    ChatSession,
    Organization,
    PersonaResponse,
    PersonaTemplate,
    Project,
    ProjectMember,
    Report,
    Simulation,
    User,
    UserSettings,
)
from app.models.enums import (
    AdInputType,
    AdStatus,
    CampaignObjective,
    ChatRole,
    PlanType,
    ProjectMemberRole,
    ProjectStatus,
    SimulationStatus,
    SimulationType,
    UserRole,
)
from app.shared.db import SessionLocal
from app.shared.security import hash_password


def U(n: int) -> uuid.UUID:
    return uuid.UUID(f"00000000-0000-0000-0000-{n:012d}")


def PID(prefix: str, n: int) -> uuid.UUID:
    return uuid.UUID(f"{prefix}-0000-0000-0000-{n:012d}")


async def seed() -> None:
    async with SessionLocal() as db:
        if (await db.execute(select(User).where(User.email == "admin@clickme.io"))).scalar_one_or_none():
            print("seed: 이미 존재 - 스킵")
            return

        admin_pw = hash_password("ChangeMe123!")
        user_pw = hash_password("Password123!")

        # ── 조직 ──
        orgs = [
            Organization(id=U(1), name="ClickMe 관리 조직", plan_type=PlanType.enterprise),
            Organization(id=U(2), name="테크스타트업", plan_type=PlanType.professional),
            Organization(id=U(3), name="마케팅에이전시", plan_type=PlanType.free),
        ]
        # ── 사용자 ──
        users = [
            User(id=U(1), organization_id=U(1), email="admin@clickme.io", password_hash=admin_pw, name="관리자", role=UserRole.admin),
            User(id=U(2), organization_id=U(2), email="kim@techstartup.io", password_hash=user_pw, name="김민준", role=UserRole.admin),
            User(id=U(3), organization_id=U(2), email="lee@techstartup.io", password_hash=user_pw, name="이서연", role=UserRole.user),
            User(id=U(4), organization_id=U(2), email="park@techstartup.io", password_hash=user_pw, name="박지훈", role=UserRole.user),
            User(id=U(5), organization_id=U(3), email="choi@agency.io", password_hash=user_pw, name="최수아", role=UserRole.admin),
        ]
        settings = [
            UserSettings(user_id=U(1), theme="dark"),
            UserSettings(user_id=U(2), theme="light"),
            UserSettings(user_id=U(3), theme="light"),
            UserSettings(user_id=U(4), theme="dark"),
            UserSettings(user_id=U(5), theme="light"),
        ]
        db.add_all(orgs + users + settings)
        await db.flush()

        # ── 프로젝트 + 멤버 ──
        projects = [
            Project(id=PID("10000000", 1), organization_id=U(2), created_by=U(2), name="여름 신제품 론칭 캠페인", description="2026년 여름 시즌 신제품 출시를 위한 광고 효과 사전 분석", status=ProjectStatus.active),
            Project(id=PID("10000000", 2), organization_id=U(2), created_by=U(3), name="앱 다운로드 전환율 캠페인", description="모바일 앱 신규 설치 유도를 위한 소셜미디어 광고 최적화", status=ProjectStatus.active),
            Project(id=PID("10000000", 3), organization_id=U(3), created_by=U(5), name="브랜드 인지도 제고 캠페인", description="신규 브랜드 런칭 인지도 광고", status=ProjectStatus.active),
        ]
        members = [
            ProjectMember(project_id=PID("10000000", 1), user_id=U(2), role=ProjectMemberRole.owner),
            ProjectMember(project_id=PID("10000000", 1), user_id=U(3), role=ProjectMemberRole.editor),
            ProjectMember(project_id=PID("10000000", 1), user_id=U(4), role=ProjectMemberRole.viewer),
            ProjectMember(project_id=PID("10000000", 2), user_id=U(3), role=ProjectMemberRole.owner),
            ProjectMember(project_id=PID("10000000", 2), user_id=U(4), role=ProjectMemberRole.editor),
            ProjectMember(project_id=PID("10000000", 3), user_id=U(5), role=ProjectMemberRole.owner),
        ]
        db.add_all(projects + members)
        await db.flush()

        # ── 광고 시안 (텍스트) ──
        ads = [
            Ad(id=PID("20000000", 1), project_id=PID("10000000", 1), created_by=U(2), name="여름 신제품 메인 카피",
               input_type=AdInputType.text,
               text_content={"headline": "올 여름, 당신의 일상을 바꿀 단 하나의 선택", "body": "새로운 라이프스타일을 위한 스마트한 제품. 지금 바로 경험해보세요.", "cta": "무료 체험 시작하기"},
               analysis_status=AdStatus.completed,
               analysis_result={"brandSafety": "safe", "emotionalTone": "positive", "keyThemes": ["혁신", "라이프스타일", "편의성"], "targetAgeGroup": "25-40", "estimatedCtr": 3.2},
               analysis_confidence=0.87),
            Ad(id=PID("20000000", 2), project_id=PID("10000000", 1), created_by=U(3), name="여름 신제품 서브 카피 A",
               input_type=AdInputType.text,
               text_content={"headline": "더위야 물렀거라! 시원한 여름 준비 완료", "body": "프리미엄 기능을 합리적인 가격에. 한정 수량 특별 할인 진행 중.", "cta": "지금 구매하기"},
               analysis_status=AdStatus.analyzing),
            Ad(id=PID("20000000", 3), project_id=PID("10000000", 2), created_by=U(3), name="앱 다운로드 유도 배너",
               input_type=AdInputType.text,
               text_content={"headline": "30초 만에 설치하고 첫 달 무료로 쓰세요", "body": "이미 50만 명이 선택한 앱. 지금 다운로드하면 프리미엄 1개월 무료 제공.", "cta": "앱 다운로드"},
               analysis_status=AdStatus.completed,
               analysis_result={"brandSafety": "safe", "emotionalTone": "neutral", "keyThemes": ["무료체험", "사회적증거", "즉시성"], "targetAgeGroup": "20-35", "estimatedCtr": 4.7},
               analysis_confidence=0.91),
        ]
        db.add_all(ads)
        await db.flush()

        # ── 페르소나 템플릿 (6 클러스터) ──
        pt = [
            ("20대 여성 직장인", "cluster_young_female_worker", {"age": 27, "gender": "female", "occupation": "직장인", "income_level": "중", "location": "서울", "lifestyle": ["SNS 활동적", "트렌드 민감", "온라인 쇼핑 선호"], "media_channels": ["인스타그램", "유튜브", "틱톡"], "pain_points": ["바쁜 일상", "가성비"], "values": ["자기계발", "워라밸"]}),
            ("30대 남성 직장인", "cluster_mid_male_worker", {"age": 34, "gender": "male", "occupation": "직장인", "income_level": "중상", "location": "경기도", "lifestyle": ["실용적 소비", "정보 수집 후 구매"], "media_channels": ["유튜브", "네이버", "카카오"], "pain_points": ["시간 부족", "신뢰성 중요"], "values": ["안정", "효율"]}),
            ("40대 여성 주부", "cluster_40s_female_homemaker", {"age": 43, "gender": "female", "occupation": "주부", "income_level": "중", "location": "서울/경기", "lifestyle": ["가족 중심", "커뮤니티 활동"], "media_channels": ["카카오톡", "네이버 카페", "유튜브"], "pain_points": ["가격 민감", "품질 중시"], "values": ["가족", "건강", "신뢰"]}),
            ("20대 남성 대학생", "cluster_young_male_student", {"age": 22, "gender": "male", "occupation": "대학생", "income_level": "하", "location": "서울", "lifestyle": ["게임", "배달음식", "구독서비스"], "media_channels": ["유튜브", "트위치", "인스타그램"], "pain_points": ["예산 한정", "가성비 극단적 중시"], "values": ["재미", "커뮤니티", "경험"]}),
            ("50대 남성 자영업자", "cluster_50s_male_selfemployed", {"age": 52, "gender": "male", "occupation": "자영업자", "income_level": "중상", "location": "지방 대도시", "lifestyle": ["오프라인 구매 선호", "입소문 중요"], "media_channels": ["네이버", "카카오", "TV"], "pain_points": ["디지털 복잡성", "사후지원"], "values": ["신뢰", "실용성", "관계"]}),
            ("30대 여성 프리랜서", "cluster_30s_female_freelancer", {"age": 31, "gender": "female", "occupation": "프리랜서", "income_level": "중", "location": "서울", "lifestyle": ["유연한 시간", "카페 작업", "온라인 커뮤니티"], "media_channels": ["인스타그램", "유튜브", "링크드인"], "pain_points": ["불안정한 수입", "자기관리"], "values": ["자유", "창의성", "성장"]}),
        ]
        db.add_all([PersonaTemplate(id=PID("30000000", i + 1), name=n, cluster_id=c, attributes=a, is_public=True) for i, (n, c, a) in enumerate(pt)])

        # ── 샘플 시뮬레이션 (완료 1건) ──
        now = datetime.now(timezone.utc)
        sim = Simulation(
            id=PID("40000000", 1), project_id=PID("10000000", 1), ad_id=PID("20000000", 1), created_by=U(2),
            simulation_type=SimulationType.ad_reaction, objective=CampaignObjective.conversion, status=SimulationStatus.completed,
            persona_count=20,
            persona_config={"ageRange": [20, 45], "genderRatio": {"female": 0.55, "male": 0.45}, "regions": ["서울", "경기", "부산"], "includeClusters": ["cluster_young_female_worker", "cluster_mid_male_worker", "cluster_30s_female_freelancer"]},
            requested_count=20, received_count=20, sample_size=20,
            results_summary={"overallScore": 74, "verdict": "긍정적 반응 우세, 구매 전환 가능성 높음", "kpi": {"attentionScore": 0.81, "sentimentScore": 0.62, "clickIntentRate": 0.60, "conversionIntentRate": 0.45, "comprehensionScore": 0.78, "recallScore": 0.71}, "topDrivers": ["감성적 카피 공감", "무료 체험 CTA 효과", "트렌디한 표현"], "topObjections": ["구체적 혜택 불명확", "제품 특성 설명 부족"]},
            llm_cost_usd=0.42, started_at=now - timedelta(days=2), completed_at=now - timedelta(days=2) + timedelta(minutes=3),
        )
        db.add(sim)
        await db.flush()

        responses_data = [
            ("persona_001", "20대 여성", {"age": 25, "gender": "female", "occupation": "직장인", "location": "서울"}, {"attention": 0.88, "sentiment": 0.75, "click_intent": True, "conversion_intent": True, "comprehension": 0.82, "recall": 0.79}, "일상 변화라는 키워드가 직접적으로 공감됨. 무료 체험 CTA가 전환 의도를 높임.", 0.91, 412, 1840),
            ("persona_002", "30대 남성", {"age": 33, "gender": "male", "occupation": "직장인", "location": "경기도"}, {"attention": 0.71, "sentiment": 0.41, "click_intent": False, "conversion_intent": False, "comprehension": 0.74, "recall": 0.65}, "카피가 감성적이라 실용적 정보가 부족하게 느껴짐. 제품 스펙 정보가 없어 구매 결정 유보.", 0.84, 398, 1720),
            ("persona_003", "20대 여성", {"age": 28, "gender": "female", "occupation": "직장인", "location": "서울"}, {"attention": 0.92, "sentiment": 0.81, "click_intent": True, "conversion_intent": True, "comprehension": 0.88, "recall": 0.83}, "트렌디한 표현과 라이프스타일 연결이 강하게 작용. 즉시 클릭 의향 높음.", 0.93, 435, 1910),
            ("persona_004", "30대 여성", {"age": 31, "gender": "female", "occupation": "프리랜서", "location": "서울"}, {"attention": 0.79, "sentiment": 0.63, "click_intent": True, "conversion_intent": False, "comprehension": 0.77, "recall": 0.72}, "클릭 의향은 있으나 무료 체험 이후 결제로 이어질지 불확실. 더 구체적인 혜택 명시 필요.", 0.87, 421, 1780),
            ("persona_005", "30대 남성", {"age": 36, "gender": "male", "occupation": "직장인", "location": "서울"}, {"attention": 0.68, "sentiment": 0.35, "click_intent": False, "conversion_intent": False, "comprehension": 0.71, "recall": 0.58}, "메시지 자체는 이해했으나 설득력 부족. 경쟁 제품 대비 차별점이 없어 보임.", 0.82, 388, 1650),
            ("persona_006", "20대 여성", {"age": 24, "gender": "female", "occupation": "대학원생", "location": "서울"}, {"attention": 0.85, "sentiment": 0.69, "click_intent": True, "conversion_intent": True, "comprehension": 0.80, "recall": 0.76}, "무료 체험이라는 진입 장벽 낮은 CTA가 효과적. 감성 카피와 연령대 일치.", 0.89, 408, 1800),
        ]
        db.add_all([
            PersonaResponse(simulation_id=PID("40000000", 1), persona_id=pid, segment=seg, persona_attributes=attr, signals=sig, reasoning=rsn, confidence=conf, llm_model="gpt-4o-mini", tokens_used=tok, response_time_ms=rt)
            for pid, seg, attr, sig, rsn, conf, tok, rt in responses_data
        ])

        db.add(Report(simulation_id=PID("40000000", 1), report_data={
            "executiveSummary": {"overallScore": 74, "verdict": "긍정적 반응 우세, 구매 전환 가능성 높음", "topPriority": "30대 남성 세그먼트 대상 실용적 정보 보강 필요"},
            "detailedAnalysis": {"kpi": {"attentionScore": 0.81, "sentimentScore": 0.62, "clickIntentRate": 0.60, "conversionIntentRate": 0.45, "comprehensionScore": 0.78, "recallScore": 0.71}, "bySegment": [{"segment": "20대 여성", "overallScore": 82, "clickIntentRate": 0.73}, {"segment": "30대 남성", "overallScore": 69, "clickIntentRate": 0.52}, {"segment": "30대 여성", "overallScore": 76, "clickIntentRate": 0.61}], "topDrivers": ["감성적 카피 공감", "무료 체험 CTA 효과", "트렌디한 표현"], "topObjections": ["구체적 혜택 불명확", "제품 특성 설명 부족", "경쟁 제품 대비 차별점 미흡"]},
            "actionItems": {"immediate": ["헤드라인에 핵심 기능 1가지 명시", "30대 남성 타겟 별도 소재 제작 검토"], "copySuggestions": ["올 여름, [핵심기능]으로 일상을 바꿔보세요"], "ctaSuggestions": ["7일 무료 체험 시작하기"], "nextABTest": "감성 카피 vs 기능 중심 카피 A/B 테스트 권장"},
        }))

        # ── 채팅 세션 + 메시지 ──
        db.add(ChatSession(id=PID("50000000", 1), user_id=U(2), project_id=PID("10000000", 1), title="여름 캠페인 시뮬레이션 결과 분석"))
        await db.flush()
        db.add_all([
            ChatMessage(session_id=PID("50000000", 1), role=ChatRole.user, content="방금 완료된 시뮬레이션 결과 요약해줘.", meta={"simulationId": str(PID("40000000", 1))}),
            ChatMessage(session_id=PID("50000000", 1), role=ChatRole.assistant, content="여름 신제품 메인 카피 시뮬레이션 결과를 요약해드릴게요.\n\n**종합 점수: 74/100** — 긍정적 반응 우세\n\n주요 KPI: 주목도 81% · 클릭 의향 60% · 전환 의향 45%", meta={"simulationId": str(PID("40000000", 1))}),
            ChatMessage(session_id=PID("50000000", 1), role=ChatRole.user, content="30대 남성 세그먼트를 위한 카피 개선안 3가지만 제안해줘.", meta=None),
            ChatMessage(session_id=PID("50000000", 1), role=ChatRole.assistant, content="30대 남성 세그먼트 맞춤 카피 개선안입니다.\n\n1. 기능 중심형\n2. 사회적 증거형\n3. 문제 해결형", meta=None),
        ])

        await db.commit()
        print("seed: 완료 - 조직3, 사용자5, 프로젝트3, 광고3, 페르소나6, 샘플시뮬1, 리포트1, 채팅1")


if __name__ == "__main__":
    asyncio.run(seed())
