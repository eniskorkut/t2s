# Antigravity Architecture: t2s Project

> **System Identity:** High-Performance Text-to-SQL RAG System
> **Core Stack:** Vanna AI (Python) | FastAPI (Async) | Next.js (App Router) | PostgreSQL

---

## 📖 1. Architectural Vision & Philosophy

This document serves as the **cognitive blueprint** for the AI Agents working on the `t2s` project. Unlike standard web applications, this project relies heavily on **Retrieval-Augmented Generation (RAG)** to convert natural language into accurate SQL queries.

### Core Principles
1.  **Accuracy First:** The primary metric of success is the validity of the generated SQL. Hallucinations are considered critical failures.
2.  **Async by Design:** Since LLM generation is I/O bound and slow, the entire backend architecture is non-blocking (Asynchronous).
3.  **Strict Separation:** Business logic, AI interaction, and API routing are strictly separated using the Service-Repository pattern.
4.  **Defensive Generation:** We assume the LLM can be tricked (Prompt Injection); therefore, validation layers exist before any SQL execution.

---

## 🏗️ 2. System Anatomy (Directory Structure)

The codebase is organized to support modular AI interactions and scalable development.

```plaintext
.agent/
├── ARCHITECTURE.md          # The Source of Truth (This file)
├── agents/                  # The "Special Forces" Team (14 Active Roles)
├── skills/                  # The Technical Knowledge Base
│   ├── vanna-rag/           # [CRITICAL] Vanna AI Training & Usage SOPs
│   ├── fastapi-expert/      # [CRITICAL] Async Backend Standards
│   ├── nextjs-react-expert/ # Frontend & UI Components
│   ├── database-design/     # SQL Schema & Normalization
│   └── ...                  # Supporting skills (Docker, Git, Security)
├── workflows/               # Automated Procedure Definitions
└── scripts/                 # Validation & Health Check Scripts

```

---

## 🤖 3. The Agent Roster (Roles & Responsibilities)

We utilize a "Special Forces" model where each agent has a strict domain of authority. Agents must **not** cross these boundaries without coordination from the Orchestrator.

### 🧠 Group A: The Core Brain (Logic & AI)

| Agent | Role Description | Primary Directive |
| --- | --- | --- |
| **`ai-engineer`** | **Guardian of the RAG Pipeline.** Manages Vanna training data (DDL, Docs), optimizes prompts, and minimizes hallucinations. | *"Ensure the model knows the schema better than the user."* |
| **`backend-specialist`** | **API Architect.** Builds high-performance FastAPI endpoints. Handles Request/Response lifecycles and strictly implements the `fastapi-expert` skill. | *"Never block the Event Loop."* |
| **`database-architect`** | **Data Sovereign.** Designs efficient PostgreSQL schemas, manages migrations, and ensures query performance (Indexing). | *"Data integrity is non-negotiable."* |

### 🎨 Group B: The Interface (Frontend & Mobile)

| Agent | Role Description | Primary Directive |
| --- | --- | --- |
| **`frontend-specialist`** | **UI Builder.** Develops Next.js (App Router) pages, React components, and handles client-side state management. | *"Make complex data look simple."* |
| **`mobile-responsive`** | **UX Guardian.** Ensures the chat interface and data tables render perfectly on mobile viewports using Tailwind CSS. | *"Mobile is not an afterthought."* |

### 🛡️ Group C: Quality & Security (Defense)

| Agent | Role Description | Primary Directive |
| --- | --- | --- |
| **`security-auditor`** | **The Shield.** Reviews code for vulnerabilities (OWASP), secure configurations, and sensitive data exposure. | *"Trust no input."* |
| **`penetration-tester`** | **The Sword.** Actively attempts to break the system using Prompt Injection, Jailbreaking, and SQL Exfiltration tactics. | *"Think like the adversary."* |
| **`qa-engineer`** | **Code Verifier.** Writes Pytest (Unit/Integration) scripts to verify backend logic and SQL generation accuracy. | *"If it's not tested, it doesn't work."* |
| **`qa-automation-engineer`** | **Flow Verifier.** Uses Playwright for End-to-End (E2E) testing of the user journey (Login -> Chat -> Result). | *"Simulate the real user."* |

### ⚙️ Group D: Operations & Management

| Agent | Role Description | Primary Directive |
| --- | --- | --- |
| **`orchestrator`** | **The Conductor.** Decomposes complex tasks, assigns them to specialists, and synthesizes the results. | *"Keep the team synchronized."* |
| **`devops-engineer`** | **Infrastructure Manager.** Manages Docker containers, `docker-compose.yml`, and deployment pipelines. | *"It works on every machine, not just mine."* |
| **`debugger`** | **Investigator.** Analyzes logs, stack traces, and error messages to find the Root Cause of failures. | *"Find the truth in the logs."* |
| **`explorer-agent`** | **The Cartographer.** Maps the codebase structure and dependencies for other agents. | *"Know the terrain."* |

---

## 🧩 4. Critical Skills (The Knowledge Base)

Agents are only as good as their instructions. We use custom "Skill" modules to enforce project standards.

### 🔥 Project-Specific Skills (High Priority)

#### **1. `vanna-rag**` (AI Engineering)

* **Purpose:** Standardizes interactions with the Vanna framework.
* **Key Rules:**
* **Training:** Priority is DDL -> Documentation -> Golden SQL.
* **Execution:** Never use `vn.ask()` in API; use `generate_sql()` -> `run_sql()`.
* **Safety:** Always validate generated SQL for destructive commands (`DROP`, `DELETE`).



#### **2. `fastapi-expert**` (Backend Engineering)

* **Purpose:** Enforces modern Python/FastAPI best practices.
* **Key Rules:**
* **Architecture:** Logic belongs in `services/`, not `routes/`.
* **Type Safety:** All inputs/outputs must be Pydantic v2 models.
* **Async:** All I/O operations must be `await`ed.



### 🔧 Core Technical Skills

* **`nextjs-react-expert`:** Server vs. Client components, Hooks, Next.js Image optimization.
* **`database-design`:** 3rd Normal Form, Foreign Key constraints, Indexing strategies.
* **`red-team-tactics`:** Knowledge of adversarial attacks on LLMs (Prompt Injection).
* **`docker-expert`:** Multi-stage builds, clean container environments.

---

## 🔄 5. Workflows & Command Protocol

Standardized procedures for common development tasks.

| Command | Workflow Description | Agents Involved |
| --- | --- | --- |
| **`/orchestrate`** | **Complex Feature Implementation.**<br>

<br>1. Explorer maps the area.<br>

<br>2. Architect plans the structure.<br>

<br>3. Specialists implement code.<br>

<br>4. QA verifies. | All |
| **`/plan`** | **Task Decomposition.**<br>

<br>Creates a step-by-step `PLAN.md` for a requested feature, identifying risks and requirements. | `orchestrator`, `explorer-agent` |
| **`/debug`** | **Incident Response.**<br>

<br>1. Reads logs.<br>

<br>2. Traces error flow.<br>

<br>3. Identifies root cause.<br>

<br>4. Suggests fix. | `debugger`, `backend-specialist` |
| **`/security-scan`** | **Vulnerability Assessment.**<br>

<br>Audits the codebase and `vanna_config.py` for security holes and prompt leakage risks. | `security-auditor`, `penetration-tester` |
| **`/train-vanna`** | **Knowledge Update.**<br>

<br>Updates the vector store with new DDL schemas or documentation. | `ai-engineer` |

---

## 🔗 6. Integration Points & Data Flow

### The "Question to Answer" Flow

1. **Frontend:** User sends question -> `POST /api/chat`
2. **Backend (Route):** Validates request (Pydantic) -> Calls Service.
3. **Backend (Service):**
* Checks Cache (Redis/Memory).
* Calls **Vanna AI** (`generate_sql`).
* **Security Check:** Scans SQL for malicious intent.
* Executes SQL (`run_sql`).


4. **Database:** Returns raw rows.
5. **Backend (Service):** Formats data (JSON/Plotly).
6. **Frontend:** Renders Table/Chart.

---

## 📊 7. Project Metrics

| Metric | Current Status |
| --- | --- |
| **Tech Stack** | Modern (2025 Standards) |
| **Agent Count** | 14 Specialized Roles |
| **Custom Skills** | 2 (`vanna-rag`, `fastapi-expert`) |
| **Primary Risk** | LLM Hallucination & Prompt Injection |

```

