<div align="center">

# ◈ Vynera — AI Workspace Platform

Build, deploy, and chat with AI employees — each one with its own knowledge base, memory, and human oversight.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)

</div>

---

## What is Vynera?

Vynera is a multi-tenant SaaS platform where teams create and manage **AI employees** — configured agents that answer questions grounded in a company's own documents, hold real conversations with memory, and route anything sensitive through a human approval step before it goes out.

It's not a chatbot wrapper. Under the hood it's two independently deployable backend services with their own databases, a real RAG pipeline with cited sources, and an audit trail for every AI-generated decision.

## Features

**🔐 Identity & Workspaces**
- JWT authentication with secure password hashing
- Multi-tenant workspaces with owner / admin / member roles
- Email-based invite → accept flow for team members

**🤖 AI Employees**
- Create, configure, and manage multiple AI agents per workspace
- Per-employee system prompt, model, and temperature
- Activate / deactivate without deleting configuration

**📚 Knowledge Base (RAG)**
- Upload PDF / DOCX documents per employee
- Automatic chunking + embedding pipeline
- Vector similarity search via pgvector — answers cite the actual source passages, not hallucinated references

**💬 Chat**
- Real-time streaming responses (SSE)
- Full conversation history, resumed on reopen
- Inline citations linking back to source documents

**✅ Human-in-the-loop Approval**
- AI-generated drafts held for review before going out
- Approve / reject with notes
- Immutable audit log of every decision

**📊 Analytics**
- Per-workspace and per-employee usage tracking
- Real token counts and cost estimation, not guesses

## Architecture

                ┌─────────────────┐
                │     Frontend      │
                │  React + Vite +   │
                │    TypeScript     │
                └────────┬─────────┘
                         │
          ┌──────────────┴──────────────┐
          │                              │
┌─────────▼─────────┐         ┌──────────▼──────────┐
│  identity-service   │         │     core-service      │
│                     │         │                       │
│  • Auth / JWT       │◄────────┤  • AI Employees       │
│  • Workspaces       │  role   │  • Knowledge Base     │
│  • Roles / Invites  │  check  │  • Chat + RAG         │
│                     │         │  • Approvals          │
│                     │         │  • Analytics          │
└─────────┬───────────┘         └──────────┬────────────┘
          │                                 │
          ▼                                 ▼
    Own database                  PostgreSQL + pgvector

Two services, two databases, no shared DB access — `core-service` verifies JWTs locally using a shared secret and calls `identity-service` only for real-time role checks. Each service can be deployed, scaled, and eventually rewritten independently.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy |
| Database | PostgreSQL, pgvector |
| Auth | JWT, Pydantic |
| LLM / Embeddings | Ollama (local, free) or Groq / Google Gemini (deployed) |
| Frontend | React, TypeScript, Vite, Tailwind CSS, TanStack Query |
| Infra | Docker |

## Project Structure

## Getting Started

Each service has its own setup instructions and `.env.example`:

```bash
# identity-service
cd identity-service
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload

# core-service (separate terminal — needs Postgres + pgvector running)
cd core-service
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8001

# frontend (separate terminal)
cd frontend
npm install
cp .env.example .env
npm run dev
```

By default, chat and embeddings run locally through [Ollama](https://ollama.com) — no API keys, no cost. See each service's `.env.example` for cloud provider alternatives (Groq, Google Gemini) when running without a local Ollama install.

## Status

Actively developed as a portfolio project. All modules above are built and manually verified end-to-end. Automated test coverage and a live deployment are in progress.