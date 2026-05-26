.PHONY: help setup setup-backend setup-frontend env-check seed seed-reset dev dev-backend dev-frontend test clean

PYTHON ?= python3
VENV   := backend/.venv
PIP    := $(VENV)/bin/pip
PY     := $(VENV)/bin/python

help: ## 사용 가능한 명령어 목록
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Setup ──────────────────────────────────────────────────────────────────
setup: setup-backend setup-frontend env-check ## 전체 의존성 설치 + .env 점검

setup-backend: ## 백엔드 venv 생성 + requirements 설치
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	@$(PIP) install --quiet --upgrade pip
	@$(PIP) install --quiet -r backend/requirements.txt
	@echo "✓ backend venv ready"

setup-frontend: ## 프론트 npm install
	@cd frontend && npm install --silent
	@echo "✓ frontend deps ready"

env-check: ## .env 필수 키 점검 (없으면 안내)
	@test -f backend/.env || (echo "✗ backend/.env 없음. cp backend/.env.example backend/.env 한 다음 값 채우세요." && exit 1)
	@grep -q "^JWT_SECRET=.\+" backend/.env || (echo "✗ backend/.env 에 JWT_SECRET 누락. 아래 명령으로 생성한 값을 채우세요:" && echo "  python3 -c 'import secrets; print(secrets.token_urlsafe(48))'" && exit 1)
	@grep -q "^NAVER_CLIENT_ID=.\+" backend/.env || echo "⚠ NAVER_CLIENT_ID 미설정 — 뉴스 검색은 실패합니다"
	@echo "✓ .env OK"

# ── Demo data ──────────────────────────────────────────────────────────────
seed: ## 데모 사용자/분석/관심종목/게시글 시드 (이미 있으면 건너뜀)
	@cd backend && ../$(PY) -m scripts.seed

seed-reset: ## 데모 데이터 비우고 새로 시드
	@cd backend && ../$(PY) -m scripts.seed --reset

# ── Dev servers ────────────────────────────────────────────────────────────
dev-backend: ## 백엔드 단독 실행 (http://localhost:8000)
	@cd backend && ../$(VENV)/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

dev-frontend: ## 프론트 단독 실행 (http://localhost:5173)
	@cd frontend && npm run dev

# 한 터미널에서 둘 다 띄우고 싶으면 별도 터미널 두 개 권장. 백그라운드 동시 실행은 로그 섞여서 비추천.

# ── Test ───────────────────────────────────────────────────────────────────
test: ## 백엔드 pytest 실행
	@cd backend && ../$(VENV)/bin/pytest -q

# ── Cleanup ────────────────────────────────────────────────────────────────
clean: ## venv / node_modules / dist 모두 삭제 (재설치하려면 다시 setup)
	rm -rf $(VENV) frontend/node_modules frontend/dist backend/redflag.db
	@echo "✓ cleaned"
