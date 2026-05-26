# News-based Stock Red Flag Detection API

## Overview

The News-based Stock Red Flag Detection API is a financial analysis system designed to identify potential corporate risks ("Red Flags") from news text.

This system integrates quantitative sentiment analysis and qualitative reasoning to provide an Explainable AI (XAI) approach to investment risk assessment.

- FinBERT: financial sentiment analysis  
- Rule-based engine: risk scoring  
- LLM: reasoning and explanation generation  

The goal is to move beyond simple scores and provide clear explanations of risk.

---

## Quick Start (시연용)

```bash
# 1. 의존성 설치 (백엔드 venv + 프론트 npm)
make setup

# 2. .env 준비 — JWT_SECRET 생성해서 넣기
cp backend/.env.example backend/.env
python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(48))" >> backend/.env
# (그 후 NAVER_CLIENT_ID/SECRET 도 채우기 — 뉴스 검색에 필수)

# 3. 데모 데이터 시드 (사용자 2명 + 분석 5건 + 관심종목 5종목 + 게시글 3건)
make seed

# 4. 서버 실행 (터미널 두 개)
make dev-backend     # http://localhost:8000  (Swagger: /docs)
make dev-frontend    # http://localhost:5173
```

**데모 계정**

| 이메일 | 비밀번호 | 용도 |
|---|---|---|
| `demo@redflag.kr` | `Demo1234!` | 분석 이력·관심종목·게시글 포함 |
| `reviewer@redflag.kr` | `Review1234!` | 빈 화면 평가용 |

**옵션 환경변수**

- `ENABLE_FINBERT=true` — 실제 FinBERT 추론 사용. 서버 시작 시 KR/EN 모델을 백그라운드로 워밍.
- `LLM_PROVIDER=anthropic` + `ANTHROPIC_API_KEY=...` — LLM 기반 설명 생성. 비워두면 한국어 템플릿 fallback.

**자주 쓰는 make 명령**

```bash
make help        # 명령어 목록
make test        # 백엔드 pytest
make seed-reset  # 데모 데이터 비우고 새로 시드
make clean       # venv / node_modules / DB 전부 삭제
```

---

## System Architecture

    Client (React)
          ↓
    FastAPI Router
          ↓
    Service Layer
          ↓
    AI Module (FinBERT + LLM)
          ↓
    Database (PostgreSQL / MongoDB)

### Design Principles

- Modular architecture for scalability  
- Layered structure for maintainability  
- Asynchronous processing for performance  

---

## Tech Stack

### Backend / AI
- Python  
- FastAPI  
- PyTorch  
- Transformers  

### Frontend
- JavaScript  
- React  

### Database
- PostgreSQL  
- MongoDB  

### Deployment
- Docker  

---

## AI Pipeline

### 1. Quantitative Sentiment Analysis
FinBERT is used to extract sentiment scores (positive, neutral, negative) from financial news text.

### 2. Risk Scoring Engine
A rule-based engine maps sentiment scores and predefined risk keywords such as:
- investigation  
- lawsuit  
- earnings decline  

into discrete risk levels:

    Low / Medium / High

### 3. Qualitative Reasoning (LLM)
The LLM interprets detected red flags and generates natural language explanations describing the underlying risk and its potential impact.

---

## Key Features

- Red Flag Detection from news text  
- Risk factor classification (regulatory, financial, legal)  
- Explainable AI reports  
- RESTful API endpoints  

---

## API Endpoints

### Analyze News

    POST /analyze

Executes the full AI pipeline on input news text.

### Get Result

    GET /results/{id}

Retrieves stored analysis results.

### Generate Report

    POST /report

Generates a summarized risk report.

---

## Testing and Quality Assurance

### Unit Testing
- Validation of risk scoring logic  
- Verification of AI output format (JSON)

### Integration Testing
- End-to-end data flow validation across FastAPI, AI modules, and database  

---

## Deployment

    docker build -t redflag-api .
    docker run -p 8000:8000 redflag-api

Docker ensures consistent runtime environments and stable execution of AI dependencies.

---

## Expected Impact

### Information Filtering
Reduces noise in financial news and highlights high-impact risk signals.

### Decision Support
Provides not only a risk score but also interpretable reasoning behind it.

### Scalability
Designed to support real-time news ingestion and multi-asset analysis in future extensions.

---

## Future Work

- Real-time news crawling and streaming analysis  
- Integration with financial data sources  
- Personalized risk profiling models  

---

## Summary

This project delivers an explainable, modular, and scalable system for extracting actionable risk insights from financial news using a hybrid AI approach.
