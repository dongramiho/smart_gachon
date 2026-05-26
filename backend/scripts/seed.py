"""
시연용 데모 데이터 시드.

사용법:
    python -m scripts.seed              # 기존 데이터 위에 ADD (이미 있는 사용자는 건너뜀)
    python -m scripts.seed --reset      # 테이블 비우고 새로 시드

데모 계정:
    demo@redflag.kr      / Demo1234!     ← 분석 5건 + 관심종목 5종목 + 게시글 3건
    reviewer@redflag.kr  / Review1234!   ← 깨끗한 평가용 계정
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from app.core.security import hash_password
from app.database import repository as repo
from app.database.models import (
    AnalysisResult,
    Comment,
    Post,
    User,
    WatchlistItem,
)
from app.database.session import SessionLocal, init_db


# ── 데모 데이터 정의 ────────────────────────────────────────────────────────
DEMO_USERS = [
    {"email": "demo@redflag.kr", "name": "데모 사용자", "password": "Demo1234!"},
    {"email": "reviewer@redflag.kr", "name": "평가 계정", "password": "Review1234!"},
]

DEMO_ANALYSES = [
    {
        "ticker": "삼성전자",
        "title": "삼성전자, 3분기 영업이익 시장 전망치 부합",
        "content": "삼성전자가 3분기 잠정 실적을 발표했다. 영업이익은 시장 컨센서스에 부합하는 수준이었다.",
        "sentiment_label": "neutral", "sentiment_score": 0.62,
        "risk_score": 22, "risk_level": "Low",
        "risk_factors": [],
        "explanation": "이 뉴스의 감성은 '중립'으로 분류되었으며 신뢰도는 0.62입니다. 산출된 위험 점수는 22/100으로 'Low' 수준에 해당합니다. 명시적인 위험 키워드는 탐지되지 않았습니다.",
    },
    {
        "ticker": "카카오",
        "title": "카카오, 공정위 조사 본격 착수… SM엔터 인수 관련",
        "content": "공정거래위원회가 카카오의 SM엔터테인먼트 인수 과정에 대한 조사에 본격 착수했다. 시세조종 의혹이 핵심 쟁점.",
        "sentiment_label": "negative", "sentiment_score": 0.91,
        "risk_score": 85, "risk_level": "High",
        "risk_factors": [
            {"category": "regulatory", "keyword": "공정위", "description": "Regulatory risk detected from investigation or penalty-related terms."},
            {"category": "regulatory", "keyword": "조사", "description": "Regulatory risk detected from investigation or penalty-related terms."},
        ],
        "explanation": "이 뉴스의 감성은 '부정'으로 분류되었으며 신뢰도는 0.91입니다. 산출된 위험 점수는 85/100으로 'High' 수준에 해당합니다. 다음과 같은 위험 신호가 탐지되었습니다: 규제 리스크('공정위'), 규제 리스크('조사'). 이는 해당 기업이 상당한 잠재 리스크에 직면해 있을 가능성을 시사합니다.",
    },
    {
        "ticker": "SK하이닉스",
        "title": "SK하이닉스, HBM 수요 폭증으로 신고가 경신",
        "content": "AI 반도체 수요가 폭증하며 SK하이닉스 주가가 신고가를 경신했다. HBM 매출 비중이 빠르게 늘고 있다.",
        "sentiment_label": "positive", "sentiment_score": 0.88,
        "risk_score": 8, "risk_level": "Low",
        "risk_factors": [],
        "explanation": "이 뉴스의 감성은 '긍정'으로 분류되었으며 신뢰도는 0.88입니다. 산출된 위험 점수는 8/100으로 'Low' 수준에 해당합니다. 명시적인 위험 키워드는 탐지되지 않았습니다.",
    },
    {
        "ticker": "현대차",
        "title": "현대차 미국 공장 노조 파업 우려… 생산 차질 가능성",
        "content": "현대차 미국 공장 노조가 임금 협상 결렬 시 파업에 돌입할 수 있다는 입장을 밝혔다.",
        "sentiment_label": "negative", "sentiment_score": 0.74,
        "risk_score": 55, "risk_level": "Medium",
        "risk_factors": [
            {"category": "management", "keyword": "파업", "description": "Management risk detected from leadership instability or misconduct."},
        ],
        "explanation": "이 뉴스의 감성은 '부정'으로 분류되었으며 신뢰도는 0.74입니다. 산출된 위험 점수는 55/100으로 'Medium' 수준에 해당합니다. 다음과 같은 위험 신호가 탐지되었습니다: 경영 리스크('파업'). 중간 수준의 불확실성이 감지되었습니다.",
    },
    {
        "ticker": "네이버",
        "title": "네이버 신규 AI 검색 베타 출시… 클릭률 상승",
        "content": "네이버가 AI 기반 검색 베타를 출시했다. 사용자 클릭률이 기존 대비 12% 상승한 것으로 나타났다.",
        "sentiment_label": "positive", "sentiment_score": 0.79,
        "risk_score": 12, "risk_level": "Low",
        "risk_factors": [],
        "explanation": "이 뉴스의 감성은 '긍정'으로 분류되었으며 신뢰도는 0.79입니다. 산출된 위험 점수는 12/100으로 'Low' 수준에 해당합니다. 명시적인 위험 키워드는 탐지되지 않았습니다.",
    },
]

DEMO_WATCHLIST = [
    {"ticker": "삼성전자", "name": "삼성전자", "memo": "주력 포지션"},
    {"ticker": "SK하이닉스", "name": "SK하이닉스", "memo": "HBM 모멘텀 관찰"},
    {"ticker": "카카오", "name": "카카오", "memo": "공정위 조사 진행 상황 확인"},
    {"ticker": "네이버", "name": "네이버", "memo": "AI 검색 베타 추이"},
    {"ticker": "현대차", "name": "현대차", "memo": "노조 협상 결과 대기"},
]

DEMO_POSTS = [
    {
        "title": "카카오 공정위 조사 어떻게 보세요?",
        "content": "오늘 카카오 관련 분석 돌렸는데 High Risk 85점 나오네요. SM엔터 인수 건이 본격 조사 들어간 거면 단기로는 보수적으로 봐야 할 듯합니다. 다른 분들 의견 궁금합니다.",
        "ticker": "카카오",
        "likes": 12,
        "comments": [
            "저도 같은 결과 받았어요. 일단 추가 매수는 보류 중입니다.",
            "공정위 조사가 실제 과징금으로 이어진 사례를 보면 단기 충격은 있지만 장기로는 회복하는 경우가 많았습니다.",
        ],
    },
    {
        "title": "SK하이닉스 HBM 모멘텀 어디까지?",
        "content": "AI 반도체 수요 자체는 견조한데, 이미 컨센서스에 많이 반영된 게 아닐까 싶기도 합니다. Red Flag 점수 8점으로 매우 낮게 나왔는데, 오히려 과열 구간 진입 신호인지 모니터링 중.",
        "ticker": "SK하이닉스",
        "likes": 8,
        "comments": [
            "메모리 사이클상 한 분기는 더 갈 수 있다고 봅니다.",
        ],
    },
    {
        "title": "현대차 미국 노조 파업 리스크",
        "content": "Medium 등급 55점. 임금 협상이 결렬되면 생산 차질이 즉각적이라 분기 실적에는 영향 클 듯합니다. 관심종목에서 일단 비중 축소했어요.",
        "ticker": "현대차",
        "likes": 5,
        "comments": [],
    },
]


# ── 시드 로직 ───────────────────────────────────────────────────────────────
def _reset_demo_tables(db) -> None:
    """데모 테이블 비우기. 운영 데이터가 섞일 수 있으니 --reset 플래그를 통해서만 호출."""
    db.query(Comment).delete()
    db.query(Post).delete()
    db.query(WatchlistItem).delete()
    db.query(AnalysisResult).delete()
    db.query(User).filter(User.email.in_([u["email"] for u in DEMO_USERS])).delete()
    db.commit()


def _ensure_user(db, *, email: str, name: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user
    user = User(email=email, name=name, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _seed_analyses(db, owner: User) -> None:
    base_time = datetime.now(timezone.utc) - timedelta(hours=len(DEMO_ANALYSES))
    for i, spec in enumerate(DEMO_ANALYSES):
        record = AnalysisResult(
            user_id=owner.id,
            ticker=spec["ticker"],
            title=spec["title"],
            content=spec["content"],
            sentiment_label=spec["sentiment_label"],
            sentiment_score=spec["sentiment_score"],
            risk_score=spec["risk_score"],
            risk_level=spec["risk_level"],
            risk_factors=spec["risk_factors"],
            explanation=spec["explanation"],
            news_link=None,
            created_at=base_time + timedelta(hours=i),
        )
        db.add(record)
    db.commit()


def _seed_watchlist(db, owner: User) -> None:
    for spec in DEMO_WATCHLIST:
        repo.add_watchlist_item(
            db,
            user_id=owner.id,
            ticker=spec["ticker"],
            name=spec["name"],
            memo=spec["memo"],
        )


def _seed_community(db, owner: User, reviewer: User) -> None:
    for spec in DEMO_POSTS:
        post = repo.create_post(
            db,
            user_id=owner.id,
            title=spec["title"],
            content=spec["content"],
            ticker=spec["ticker"],
        )
        # 좋아요 카운트 직접 세팅 — repo.like_post를 N번 호출해도 되지만 시드 단계에선 직접 갱신.
        post.likes = spec["likes"]
        db.commit()
        for comment_text in spec["comments"]:
            repo.add_comment(db, post_id=post.id, user_id=reviewer.id, content=comment_text)


def run(reset: bool = False) -> None:
    init_db()
    db = SessionLocal()
    try:
        if reset:
            print("→ --reset: 데모 테이블 비우는 중…")
            _reset_demo_tables(db)

        users = {}
        for spec in DEMO_USERS:
            user = _ensure_user(db, email=spec["email"], name=spec["name"], password=spec["password"])
            users[spec["email"]] = user
            print(f"✓ user: {user.email} (id={user.id})")

        owner = users["demo@redflag.kr"]
        reviewer = users["reviewer@redflag.kr"]

        existing_analyses = db.query(AnalysisResult).filter(AnalysisResult.user_id == owner.id).count()
        if existing_analyses == 0:
            _seed_analyses(db, owner)
            print(f"✓ analyses: {len(DEMO_ANALYSES)}건")
        else:
            print(f"· analyses: 이미 {existing_analyses}건 존재 — 건너뜀")

        existing_watch = repo.get_watchlist(db, owner.id)
        if not existing_watch:
            _seed_watchlist(db, owner)
            print(f"✓ watchlist: {len(DEMO_WATCHLIST)}종목")
        else:
            print(f"· watchlist: 이미 {len(existing_watch)}건 존재 — 건너뜀")

        existing_posts = db.query(Post).count()
        if existing_posts == 0:
            _seed_community(db, owner, reviewer)
            print(f"✓ community: {len(DEMO_POSTS)}게시글 + 댓글")
        else:
            print(f"· community: 이미 {existing_posts}건 존재 — 건너뜀")

        print()
        print("== 로그인 정보 ==")
        for spec in DEMO_USERS:
            print(f"  {spec['email']:<25} / {spec['password']}")

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true", help="기존 데모 데이터를 비우고 다시 생성")
    args = parser.parse_args()
    run(reset=args.reset)
