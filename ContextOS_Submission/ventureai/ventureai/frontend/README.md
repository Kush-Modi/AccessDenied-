# ContextOS
## Enterprise AI Operating System for Workforce Intelligence

> *The Context Layer for Workforce Intelligence*

[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-ReAct-6366f1)](https://langchain-ai.github.io/langgraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## What is ContextOS?

ContextOS is not a recruiter dashboard. It is an **Enterprise AI Operating System** — a complete decision intelligence platform that transforms raw workforce context (meeting notes, CRM updates, emails, recruiter observations) into precise, explainable placement recommendations via a multi-agent AI pipeline.

Where traditional ATS software stores data, ContextOS understands it.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ContextOS Frontend                               │
│                    Next.js 15 · React 19 · Tailwind v4                  │
│                    Framer Motion · React Flow · SWR                      │
│           http://localhost:3000  ←→  REST API                           │
└───────────────────────────┬─────────────────────────────────────────────┘
                            │ HTTP REST (JSON)
┌───────────────────────────▼─────────────────────────────────────────────┐
│                         FastAPI Gateway                                  │
│                           main.py · :8000                                │
│                                                                          │
│  GET  /health              GET  /candidates      GET  /clients           │
│  POST /analyze             GET  /hitl/pending    POST /hitl/respond      │
│  GET  /nba/queue           GET  /logs/{id}       POST /analyze/outcome   │
└───────────────────────────┬─────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────────────┐
│                      LangGraph ReAct Agent                               │
│                           agent.py                                       │
│                                                                          │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐             │
│  │  run_llm     │  │  call_tools   │  │ format_recommend │             │
│  │  _agent      │→ │  (MCP calls)  │→ │ ation            │             │
│  └──────────────┘  └───────────────┘  └────────┬─────────┘             │
│                                                  │                       │
│  ┌──────────────────────────────────────────────▼─────────────────────┐ │
│  │                        hitl_gate                                   │ │
│  │            interrupt() → MemorySaver checkpoint                    │ │
│  └──────────────────────────────────────────────┬─────────────────────┘ │
│                                                  │ Command(resume=...)   │
│  ┌───────────────────────────────────────────────▼─────────────────────┐ │
│  │                       execute_action                                │ │
│  │         approved → Supabase log + Redis NBA cache                  │ │
│  │         rejected → Supabase log + Redis status                     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────────────┘
                            │  stdio transport
┌───────────────────────────▼─────────────────────────────────────────────┐
│                      FastMCP Server (mcp_server.py)                      │
│                                                                          │
│  get_candidate_profile()         get_client_account_health()            │
│  search_job_descriptions()       get_placement_history()                 │
│  log_recruiter_action()                                                  │
└────────────┬──────────────────────────────────────────────┬─────────────┘
             │                                              │
┌────────────▼─────────────┐              ┌────────────────▼─────────────┐
│      Supabase             │              │          Redis                │
│  PostgreSQL + pgvector    │              │   Cache · Session · HITL      │
│                           │              │                               │
│  Tables:                  │              │  Keys:                        │
│  - candidates             │              │  - nba:{candidate_id}        │
│  - clients                │              │  - hitl_pending:{session}    │
│  - job_descriptions       │              │  - hitl_decision:{session}   │
│  - knowledge_items        │              │  - session_logs:{session}    │
│  - recruiter_actions      │              │                               │
│  - placement_outcomes     │              │                               │
└───────────────────────────┘              └───────────────────────────────┘
```

---

## Intelligence Pipeline

The system executes a 7-layer intelligence pipeline for every candidate evaluation:

```
[1] Candidate Profile
      ↓  get_candidate_profile() via MCP
[2] Enterprise Knowledge Agent
      ↓  Hybrid Retrieval: Semantic → Metadata Filter → Multi-Signal Rank → Lexical Rerank
[3] Planner Memory
      ↓  FeedbackLearner.analyze_history() — historical placement outcomes
[4] Business Rules Engine
      ↓  12 rules: BLOCK / SUPPRESS / INCREASE / DECREASE confidence
[5] Action Planner Agent
      ↓  LLM structured output (MatchRecommendation) + confidence rubric
[6] Decision Intelligence (DecisionScorer)
      ↓  Multi-signal: 35% fit + 25% RAG + 20% memory + 10% health + 10% priority
[7] Explainability Formatter
      ↓  Evidence tree, knowledge trace, decision trace, business rule trace
[8] HITL Gate
      ↓  interrupt() → Redis pending → Frontend approval → Command(resume=)
[9] Action Execution
      ↓  Supabase log + Redis NBA cache
```

### Confidence Score Formula

```
Base Score =
    (0.35 × candidate_fit_score)
  + (0.25 × top_knowledge_score)
  + (0.20 × memory_score)
  + (0.10 × client_health)
  + (0.10 × priority_urgency_score)

Final Confidence = Base Score + sum(business_rule_adjustments)
                  clamped to [0.0, 1.0]
```

Weights are configurable via `config/` and loaded at runtime by `ConfigLoader`.

---

## Business Rules Engine

Located in `business_rules/rules.yaml`. 12 active rules:

| Rule ID | Condition | Action | Weight |
|---|---|---|---|
| RULE_CLIENT_HEALTH_LOW | client_health < 40% | decrease_confidence | -0.15 |
| RULE_RECENT_REJECTION | candidate_rejected_recently | block | -1.0 |
| RULE_ALREADY_SUBMITTED | candidate_already_submitted | suppress | -1.0 |
| RULE_HIRING_FREEZE | hiring_freeze | block | -1.0 |
| RULE_HIGH_PRIORITY_CLIENT | high_priority_client | increase_confidence | +0.10 |
| RULE_NOTICE_PERIOD_LONG | notice_period > 60 days | decrease_confidence | -0.10 |
| RULE_UNAVAILABLE | candidate_unavailable | block | -1.0 |
| RULE_URGENT_HIRING | urgent/critical job | increase_confidence | +0.10 |
| RULE_DUPLICATE_REC | duplicate_recommendation | suppress | -0.50 |
| RULE_SALARY_MISMATCH | salary_mismatch | decrease_confidence | -0.20 |
| RULE_LOCATION_MISMATCH | location_mismatch (not remote) | decrease_confidence | -0.15 |
| RULE_MISSING_MANDATORY_SKILLS | missing critical skills | decrease_confidence | -0.25 |

---

## Knowledge Layer

The `knowledge/` module implements a full **Hybrid Retrieval** pipeline:

1. **Embedding** — `embedder.get_embedding(query_text)` generates a vector
2. **Vector Search** — Supabase pgvector `match_knowledge_items()` returns up to 100 results
3. **Metadata Filtering** — `filter_by_metadata()` scopes to candidate/client entity
4. **Similarity Threshold** — `filter_by_similarity()` applies configurable cutoff (default 0.75)
5. **Multi-Signal Ranking** — `rank_items()` applies composite scoring
6. **Lexical Reranking** — `rerank_items()` boosts keyword matches in query
7. **Top-K Selection** — Returns top 5 results (configurable)

Knowledge types: `meeting_note`, `crm_update`, `email`, `recruiter_note`, `interview_feedback`, `customer_interaction`, `playbook`

---

## Frontend Pages

| Route | Page Name | Description |
|---|---|---|
| `/` | Landing Page | Editorial hero, architecture flow, tech stack |
| `/command-center` | AI Command Center | Candidate workspace, HITL gate, NBA queue |
| `/command-center/planner` | AI Planner | Full-screen React Flow graph of LangGraph architecture |
| `/command-center/candidates` | Candidate Intelligence | List with search/filter + skill chips |
| `/command-center/candidates/[id]` | Candidate Profile | Tabs: Overview, Skills, Timeline, Memory, Recommendations |
| `/command-center/clients` | Client Intelligence | Health rings, priority status, hiring freeze indicators |
| `/command-center/decision-queue` | Decision Queue | Ranked NBA feed, confidence rings, auto-sync |
| `/command-center/execution-timeline` | Execution Timeline | GitHub activity-style knowledge log with filter |
| `/command-center/analytics` | Decision Analytics | 8 metrics, sparklines, business rules breakdown |
| `/command-center/platform-health` | Platform Health | Vercel-style service status with auto-refresh |
| `/command-center/settings` | Platform Configuration | API config, decision weights, retrieval config |

---

## Frontend Features

### UX / Interaction
- **Boot Screen** — Sequential initialization reveal (Planner → Knowledge → Redis → Rules → Memory → Embeddings)
- **Command Palette** — `Cmd/Ctrl+K` — search candidates, clients, jobs, navigate pages (Linear-style)
- **Resizable Sidebar** — Drag the sidebar edge to resize (VS Code style)
- **Keyboard Shortcuts** — `A` = Analyze, `Ctrl+K` = Search, `Esc` = Close panels
- **Optimistic UI** — Approve/Reject shows instant feedback before server response
- **Auto-sync Indicators** — "Auto-syncing every 5s" on Decision Queue; "Last checked" on Platform Health
- **Toast Notifications** — 4-second auto-dismiss for all actions
- **Notifications Panel** — Recent approvals, recommendations, system events in top navbar
- **Profile Menu** — Recruiter profile, settings, sign-out in top-right navbar

### Design
- **Dark-first** — `#09090B` background, `#111113` cards, `#26272B` borders
- **Grain texture** — Subtle animated noise overlay for editorial depth
- **Gradient orbs** — Animated indigo/violet blob backgrounds
- **Glassmorphism** — `backdrop-blur` + subtle borders on all cards
- **Framer Motion** — Page transitions, stagger reveals, card flips, layout animations
- **React Flow** — Animated AI Planner node graph with custom glassmorphic nodes
- **Skeleton loaders** — Everywhere instead of spinners
- **Confidence rings** — SVG arc with animated fill and color-coded thresholds
- **Evidence Cards** — Apple-quality 5-layer breakdown with animated progress bars

### Accessibility
- `aria-label` on all interactive elements
- `aria-current="page"` on active nav items
- `role="dialog"`, `role="listbox"`, `role="option"` on command palette
- `focus-visible` ring: `outline: 2px solid #6366f1`
- `prefers-reduced-motion` — disables all animations for users who prefer it
- Keyboard navigation throughout command palette and sidebar

---

## Getting Started

### Prerequisites
- Node.js 18+ (tested on v22.11.0)
- Python 3.11+
- Redis running locally or via cloud
- Supabase project with schema migrated

### 1. Start the Backend

```bash
cd ventureai/ventureai
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your Supabase + Redis + Groq credentials

# Start FastAPI
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend available at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### 2. Start the Frontend

```bash
cd ventureai/ventureai/frontend
npm install
npm run dev
```

Frontend available at: `http://localhost:3000`

### 3. (Optional) Legacy Streamlit UI

```bash
cd ventureai/ventureai
streamlit run app_streamlit.py
```

Streamlit dashboard available at: `http://localhost:8501`

---

## Environment Variables

### Backend (`.env`)
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
REDIS_URL=redis://localhost:6379
GROQ_API_KEY=gsk_...
```

### Frontend (optional `.env.local`)
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

---

## Project Structure

```
ventureai/
├── ventureai/                    ← Backend (Python / FastAPI)
│   ├── main.py                   ← FastAPI REST API (9 endpoints)
│   ├── agent.py                  ← LangGraph ReAct agent graph
│   ├── mcp_server.py             ← FastMCP server (5 tools, stdio)
│   ├── mcp_client.py             ← MCP client wrapper
│   ├── redis_client.py           ← Redis cache + HITL + session logs
│   ├── supabase_client.py        ← Supabase PostgreSQL client
│   ├── app_streamlit.py          ← Legacy Streamlit UI (preserved)
│   ├── agents/
│   │   ├── action/               ← ActionPlannerAgent (scoring + explainability)
│   │   ├── candidate/            ← CandidateAgent
│   │   ├── client/               ← ClientAgent
│   │   ├── knowledge/            ← KnowledgeAgent (hybrid retrieval)
│   │   └── planner/              ← PlannerAgent
│   ├── business_rules/
│   │   ├── rules.yaml            ← 12 configurable rules
│   │   ├── engine.py             ← Rule evaluation engine
│   │   ├── evaluator.py          ← Context builder
│   │   └── loader.py             ← YAML loader
│   ├── knowledge/
│   │   ├── knowledge_service.py  ← Hybrid search orchestration
│   │   ├── knowledge_models.py   ← Pydantic models (7 types)
│   │   └── repository.py         ← Supabase queries
│   ├── memory/
│   │   ├── planner_memory.py     ← Memory context retrieval
│   │   ├── learning.py           ← FeedbackLearner analytics
│   │   ├── feedback_manager.py   ← Outcome recording
│   │   └── repository.py         ← Supabase feedback queries
│   ├── retrieval/
│   │   ├── filters.py            ← Metadata + similarity filtering
│   │   ├── ranking.py            ← Multi-signal ranking
│   │   ├── reranker.py           ← Lexical reranking
│   │   └── metrics.py            ← Retrieval performance metrics
│   ├── explainability/
│   │   ├── scoring.py            ← DecisionScorer (multi-signal formula)
│   │   ├── formatter.py          ← Evidence tree + trace generation
│   │   └── evidence.py           ← EvidenceNode model
│   ├── embeddings/               ← Embedding utilities
│   ├── core/
│   │   ├── execution/            ← Agent execution context
│   │   ├── registry/             ← BaseAgent registry
│   │   ├── state/                ← Shared state management
│   │   ├── llm_client.py         ← Groq LLM + MatchRecommendation schema
│   │   └── config_loader.py      ← YAML config loader
│   ├── config/                   ← Decision weights, retrieval config
│   ├── demo_data/                ← Scenario factory + generators
│   └── tests/                   ← 7 test suites
│
└── frontend/                     ← ContextOS Frontend (Next.js 15)
    ├── app/
    │   ├── globals.css            ← Design system (tokens, animations)
    │   ├── layout.tsx             ← Root layout + fonts
    │   ├── page.tsx               ← Landing page (boot screen + 7 sections)
    │   └── command-center/
    │       ├── layout.tsx         ← Dashboard shell
    │       ├── page.tsx           ← AI Command Center
    │       ├── planner/           ← AI Planner (React Flow)
    │       ├── candidates/        ← Candidate Intelligence
    │       ├── clients/           ← Client Intelligence
    │       ├── decision-queue/    ← Decision Queue
    │       ├── execution-timeline/← Execution Timeline
    │       ├── analytics/         ← Decision Analytics
    │       ├── platform-health/   ← Platform Health
    │       └── settings/          ← Platform Configuration
    ├── components/
    │   ├── BootScreen.tsx         ← Startup initialization screen
    │   ├── Sidebar.tsx            ← Navigation with active state animation
    │   ├── Navbar.tsx             ← Breadcrumbs + notifications + profile
    │   ├── CommandPalette.tsx     ← Cmd+K search palette
    │   ├── DashboardShell.tsx     ← Resizable sidebar shell
    │   ├── landing/               ← 7 landing page sections
    │   └── command-center/
    │       ├── ConfidenceRing.tsx ← SVG animated confidence arc
    │       └── EvidenceCards.tsx  ← Apple-quality 5-layer evidence breakdown
    ├── lib/
    │   ├── api.ts                 ← Typed API fetch wrappers
    │   └── utils.ts               ← cn(), formatters, color helpers
    └── types/
        └── index.ts               ← All TypeScript interfaces
```

---

## API Reference

All endpoints served by FastAPI at `http://localhost:8000`:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | System health check |
| `GET` | `/candidates` | List all candidates from Supabase |
| `GET` | `/clients` | List all clients from Supabase |
| `GET` | `/jobs` | List all job descriptions with client names |
| `POST` | `/analyze` | Trigger LangGraph agent for a candidate |
| `GET` | `/hitl/pending/{session_id}` | Get pending HITL approval card |
| `POST` | `/hitl/respond` | Submit approve/reject decision |
| `GET` | `/nba/queue` | Get ranked approved recommendations from Redis |
| `GET` | `/logs/{session_id}` | Get agent execution logs from Redis |
| `POST` | `/analyze/outcome` | Record placement outcome for memory learning |

Interactive API docs: `http://localhost:8000/docs`

---

## Key Design Decisions

### Why LangGraph?
LangGraph's stateful graph with `MemorySaver` checkpointing enables the HITL interrupt pattern — the agent can pause mid-execution, wait for human approval, and resume deterministically from the exact checkpoint.

### Why MCP?
The Model Context Protocol provides a clean separation between the agent brain (`agent.py`) and data access. The agent never touches Supabase directly — it calls MCP tools, which handle all database operations. This makes the system auditable and tool-replaceable.

### Why Redis for HITL?
The HITL gate stores the pending recommendation in Redis so the frontend can poll for it independently of the LangGraph state. This decouples the UI polling from the agent's internal state machine.

### Why Hybrid Retrieval?
Pure vector search misses exact keyword matches. Pure BM25 misses semantic similarity. The hybrid pipeline (embed → metadata filter → multi-signal rank → lexical rerank) captures both, giving better results than either alone.

### Why not modify the Streamlit UI?
The Streamlit UI (`app_streamlit.py`) is preserved as a functional legacy/demo interface. The new Next.js frontend communicates exclusively via the REST API — zero coupling to Streamlit, zero backend changes required.

---

## Testing

```bash
cd ventureai/ventureai

# All tests
pytest tests/ -v

# Specific suites
pytest tests/test_api.py -v           # REST API integration
pytest tests/test_agent_flow.py -v   # LangGraph graph nodes
pytest tests/test_mcp.py -v          # MCP tool calls
pytest tests/test_redis.py -v        # Redis operations
pytest tests/test_supabase.py -v     # Database connectivity
```

---

## Built For

XLVentures Hackathon 2026  
Enterprise Decision Intelligence Track

---

*ContextOS — Enterprise AI Operating System · The Context Layer for Workforce Intelligence*
