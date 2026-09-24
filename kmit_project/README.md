# 🛡️ SpendGuardian AI: Autonomous Subscription & Recurring-Spend Guardian Agent

> **PRAGYAAN 2.0 Hackathon | Department of CSE (AI&ML), Keshav Memorial Institute of Technology (KMIT)**  
> **Problem Statement 6:** *Subscription & Recurring-Spend Guardian Agent*  
> *Find the money you're quietly leaking every month — and stop it, autonomously.*

---

## 📑 Table of Contents
1. [Project Overview](#1-project-overview)
2. [What All Technology is Involved](#2-what-all-technology-is-involved)
3. [Why Did We Choose This Specific Technology Stack?](#3-why-did-we-choose-this-specific-technology-stack)
4. [Complete Project Workflow & Architecture](#4-complete-project-workflow--architecture)
5. [The Core Pillars: Detect → Decide → Act](#5-the-core-pillars-detect--decide--act)
6. [Why This is Truly Agentic AI (Not Just a Classifier)](#6-why-this-is-truly-agentic-ai-not-just-a-classifier)
7. [Deterministic Guardrails: The Safety Core](#7-deterministic-guardrails-the-safety-core)
8. [Sample Scenarios & Problem Statement Validation](#8-sample-scenarios--problem-statement-validation)
9. [Bonus & Stretch Capabilities Implemented](#9-bonus--stretch-capabilities-implemented)
10. [Folder Structure & Code Organization](#10-folder-structure--code-organization)
11. [How to Run, Test, and Demonstrate](#11-how-to-run-test-and-demonstrate)

---

## 1. Project Overview

Modern consumers and businesses quietly leak hundreds to thousands of dollars/rupees every month through:
* Forgotten free trials that silently convert to high-cost recurring paid subscriptions.
* Unscheduled or stealthy 15–25% price hikes from service providers.
* Overlapping and redundant services in identical functional categories (e.g., paying for TuneWave and MusicBox simultaneously).
* Unused memberships (e.g., gym memberships untouched for 90–180 days).
* Standalone subscriptions that are already included for free within an active bundle (e.g., paying separately for Spotify while subscribed to YouTube Premium which already includes YouTube Music).

Traditional personal finance apps merely categorize past spending on static charts; they require users to manually scrutinize line items, and they take zero action. 

**SpendGuardian AI** is an autonomous, agentic AI financial assistant that **scans transaction and email history**, **detects periodic recurring cadences**, **evaluates usage-based waste and decision confidence**, **enforces strict user-defined safety guardrails**, **autonomously pauses or cancels low-risk wasteful subscriptions**, and **escalates ambiguous decisions to the user with plain-language reasoning**.

---

## 2. What All Technology is Involved

The system is constructed with a modern, production-ready decoupled architecture:

### 🎨 Frontend (Financial Command Center)
* **React 18**: Component-driven UI framework for dynamic, reactive state management and instantaneous updates.
* **Vite 6**: Ultra-fast build tool and development server with Hot Module Replacement (HMR).
* **Tailwind CSS 3**: Modern utility-first styling system configured with a dark financial control center theme.
* **Lucide React**: Iconography suite for crisp visual indicators, badges, and telemetry icons.
* **Axios**: HTTP client with request/response interceptors communicating with the backend REST APIs.

### ⚙️ Backend (Autonomous Agent Engine)
* **Python 3.12**: Core backend language chosen for high-performance financial data modeling and native AI integration.
* **FastAPI**: Modern, asynchronous web framework providing high throughput, type validation, and auto-generated interactive OpenAPI/Swagger documentation (`/docs`).
* **Uvicorn**: Lightning-fast ASGI web server.
* **Pydantic v2**: High-performance data parsing, strict typing, and validation schemas for requests, responses, and guardrail policies.
* **SQLAlchemy 2.0**: Enterprise ORM facilitating database abstraction, relational models, and cascading integrity.
* **SQLite**: Embedded database engine providing ACID transactions and zero-dependency local setup.
* **Pandas & NumPy**: High-speed numerical calculations, timestamp delta mathematics, and cadence clustering.

### 🧠 AI & Agentic Orchestration Layer
* **Agent Orchestrator Pipeline**: Central coordinator executing the multi-stage lifecycle: Perceive → Detect → Decide → Check Guardrails → Act → Audit.
* **TransactionParser Sub-Agent**: Cadence interval engine that clusters transactions by merchant and calculates date deltas (weekly, monthly, quarterly, yearly).
* **EmailAnalyzer Sub-Agent**: Natural language email scanner extracting price-change notices, free-trial expirations, and renewal invoices.
* **WasteAnalyzer Engine**: Explainable 6-factor waste scoring algorithm (0–100).
* **ConfidenceEngine**: Decision certainty assessment engine (0.0–1.0) flagging ambiguous preference dilemmas.
* **GuardrailEngine**: Deterministic safety policy governor enforcing spending ceilings, protected categories whitelist, and human-in-the-loop approvals.
* **BundleDetector Sub-Agent**: Cross-referencing engine detecting redundant standalone tools covered by existing bundled suites (e.g., YouTube Premium covering music).
* **PriceHikeDetector & Predictor**: Detects delta price increases and flags annual renewal risk cycles.
* **NegotiationAgent**: Retention pitch generation and counter-offer acceptance simulator.
* **ActionExecutor & Audit Ledger**: Autonomous execution module with cryptographic action logging and realization of monthly/annual savings.
* **Dual-Mode LLM Provider**: Supports both an instant, 100% offline rule-and-NLP heuristic agent (zero API keys needed) and dynamic external LLM integration (OpenAI / Gemini).

### 🧪 Testing & Verification
* **Pytest**: Automated test runner.
* **In-Memory SQLite Suite**: Isolated test fixtures for deterministic end-to-end pipeline verification.

---

## 3. Why Did We Choose This Specific Technology Stack?

During hackathons and production development, architectural decisions define whether a project succeeds or fails. Below is the technical rationale for why we chose this specific stack over alternatives:

### 1. Why FastAPI + Python (Instead of Node.js / Express or Django)?
| Criteria | FastAPI + Python | Node.js / Express | Django |
| :--- | :--- | :--- | :--- |
| **Data Manipulation & Time Math** | **Native Pandas/NumPy** provides date delta operations, mean cadence calculations, and statistical clustering in microseconds. | Requires manual JavaScript date manipulation or heavy external libraries (`date-fns`, `moment`). | Python-based, but overly heavy for microservice APIs. |
| **Speed & Async Concurrency** | **Asynchronous ASGI** architecture built on Starlette and Pydantic makes it one of the fastest Python frameworks available. | Fast async event loop, but lacks native machine learning and data science ecosystem. | Synchronous WSGI by default; heavyweight overhead. |
| **API Contract & Documentation** | **Auto-generates OpenAPI (Swagger UI) at `/docs`** directly from Pydantic models. Evaluators can test any endpoint in browser without Postman. | Requires manual Swagger JSDoc comments or external tools. | Requires DRF (Django REST Framework) and extra swagger packages. |
| **AI/Agent Integration** | Python is the undisputed lingua franca of AI, LangChain, LangGraph, and LLM APIs. | Node LLM libraries lag behind Python implementations. | Good AI support, but high boilerplate. |

### 2. Why React + Vite (Instead of Server-Side Rendering or Vanilla JS)?
* **Real-Time Agent Telemetry**: When the autonomous agent audits subscriptions, it streams step-by-step reasoning traces (`[PERCEIVE]`, `[DETECT]`, `[REASON]`, `[GUARDRAIL]`, `[ACT]`). React's reactive state engine updates the UI and terminal immediately without page reloads.
* **Vite's Instant HMR**: Zero-lag compilation with native ES modules delivers sub-second feedback during live demonstration and evaluation.
* **Component Modularity**: Allows separate, clean components for the Agent Terminal, Approvals Section, Guardrails Policy Modal, Subscription Cards, and Negotiation Dialogue.

### 3. Why SQLite with SQLAlchemy ORM (Instead of MongoDB or PostgreSQL)?
* **Zero-Configuration Reliability**: MongoDB and PostgreSQL require background service daemons (`mongod`, `systemctl start postgresql`). If a judging environment or team member's machine lacks running database daemons, the app crashes. SQLite runs anywhere with zero setup.
* **Relational Integrity**: Financial data is inherently relational: a `User` has `Guardrails`, `Transactions`, `Subscriptions`, and `ActionLogs`. Foreign keys and cascading relationships in SQLAlchemy guarantee data consistency.

### 4. Why Dual-Mode Agentic Architecture (Deterministic Code + LLM)?
A common mistake in hackathons is relying on a single massive LLM prompt to do everything: parse transactions, do math, compute intervals, check limits, and take action. 
* **The Problem with LLMs for Everything**: LLMs suffer from math hallucinations, non-deterministic outputs, and token latency. You cannot risk having an LLM hallucinate that ₹2,500 is less than ₹2,000, or forget that Insurance is protected.
* **Our Solution**:
  * **Traditional Code Handles**: Deterministic tasks (date difference calculations, recurring clustering, percentage increase math, waste scoring, and strict guardrail enforcement).
  * **LLM Handles**: Semantic tasks (understanding unstructured billing email notifications, generating plain-language reasoning explanations, and drafting polite negotiation letters).
* **The Result**: 100% deterministic safety, zero hallucinations on financial numbers, explainable reasoning, and instant offline execution.

---

## 4. Complete Project Workflow & Architecture

The following diagram illustrates the complete end-to-end data flow:

```
                          ┌───────────────────────────┐
                          │           USER            │
                          │   "Clean my subscriptions"│
                          └─────────────┬─────────────┘
                                        │
                                        ▼
                          ┌───────────────────────────┐
                          │   AI AGENT ORCHESTRATOR   │
                          │        (Agent Brain)      │
                          └─────────────┬─────────────┘
                                        │
             ┌──────────────────────────┼──────────────────────────┐
             ▼                          ▼                          ▼
   ┌───────────────────┐      ┌───────────────────┐      ┌───────────────────┐
   │Transaction Parser │      │   Email Analyzer  │      │  Guardrail Config │
   │   (Bank Feeds)    │      │  (Billing Alerts) │      │ (Safety Limits &  │
   └─────────┬─────────┘      └─────────┬─────────┘      │ Protected Whitelist│
             │                          │                └─────────┬─────────┘
             └──────────────────────────┼──────────────────────────┘
                                        ▼
                          ┌───────────────────────────┐
                          │   RECURRING CADENCE &     │
                          │     DETECTION ENGINE      │
                          │ (Weekly, Monthly, Yearly) │
                          └─────────────┬─────────────┘
                                        ▼
                          ┌───────────────────────────┐
                          │   INTELLIGENCE LAYER      │
                          │ • Price Hike Detector     │
                          │ • Free-Trial Detector     │
                          │ • Bundle Redundancy Check │
                          │ • Multi-Factor Waste (0-100)│
                          │ • Confidence Engine (0-100%)│
                          └─────────────┬─────────────┘
                                        ▼
                          ┌───────────────────────────┐
                          │  DETERMINISTIC GUARDRAIL  │
                          │      POLICY ENGINE        │
                          └─────────────┬─────────────┘
                                        │
                  ┌─────────────────────┼─────────────────────┐
                  │                     │                     │
                  ▼                     ▼                     ▼
         [PASSED GUARDRAILS]     [AMBIGUOUS OVERLAP]   [STRICTLY BLOCKED]
          Waste ≥ 70 & < Limit    Duplicate Services    Protected Category
                  │                     │               (e.g., Insurance)
                  ▼                     ▼                     ▼
          ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
          │  AUTO-CANCEL  │     │  ESCALATE TO  │     │ BLOCK AUTONOMY│
          │  (Zero Risk)  │     │     HUMAN     │     │ (Safety Lock) │
          └───────┬───────┘     └───────┬───────┘     └───────┬───────┘
                  │                     │                     │
                  └─────────────────────┼─────────────────────┘
                                        ▼
                          ┌───────────────────────────┐
                          │     ACTION EXECUTOR &     │
                          │  IMMUTABLE AUDIT LEDGER   │
                          └─────────────┬─────────────┘
                                        ▼
                          ┌───────────────────────────┐
                          │     FINANCIAL CONTROL     │
                          │     CENTER DASHBOARD      │
                          │ (Realized Savings Report) │
                          └───────────────────────────┘
```

---

## 5. The Core Pillars: Detect → Decide → Act

### Pillar 1: DETECT
* **Recurring Charges**: Groups transactions by merchant and calculates consecutive interval deltas. Intervals clustered around 7 days → Weekly; ~30 days → Monthly; ~90 days → Quarterly; ~365 days → Yearly.
* **Free-Trial-to-Paid Conversions**: Detects ₹0 / $0 trial authorizations or trial emails followed 14–30 days later by full recurring subscription fees.
* **Price Hikes vs. Last Billed**: Detects price changes between billing cycles and calculates the exact percentage jump (e.g., Canva Pro increasing from ₹499 to ₹599, +20%).
* **Duplicate / Overlapping Services**: Identifies multiple active subscriptions occupying the same functional category (e.g., TuneWave and MusicBox both in `music_streaming`).
* **Bundle Redundancy**: Recognizes when an active comprehensive bundle (e.g., YouTube Premium, Amazon Prime, Apple One) already covers a service the user is paying for as a standalone subscription.

### Pillar 2: DECIDE
* **Multi-Factor Waste Score (0–100)**:
  * Inactivity Duration: 180+ days inactive (+75 pts); 90+ days (+50 pts); 60+ days (+35 pts); 30+ days (+20 pts); ≤7 days (0 pts / Active).
  * Inactive recurring penalty (+15 pts).
  * Duplicate service with lower usage (+20 pts).
  * Unused converted free trial (+20 pts).
  * Bundle redundancy (+20 pts).
  * Unscheduled price hike (+15 pts).
  * High monthly cost (+10 to +15 pts).
* **Confidence Score (0.0–1.0 / 0%–100%)**:
  * Unambiguous single services with long inactivity receive high confidence (0.95–0.98).
  * Competing services in the same category where both have recent usage receive lower confidence (0.65) because the agent cannot assume personal preference.
* **LLM Plain-Language Rationale**: Generates transparent, human-readable explanations explaining why an action was taken or escalated.

### Pillar 3: ACT
* **Auto-Cancel**: Automatically revokes mandates on zero-risk, high-waste, non-protected subscriptions under the spending ceiling.
* **Auto-Downgrade**: Recommends tier downgrade when premium features are unutilized.
* **Human-in-the-Loop Escalation**: Surfaces interactive approval cards with side-by-side usage metrics for ambiguous decisions.
* **Negotiation Mode**: Generates professional merchant retention inquiries and handles simulated loyalty counter-offers (e.g., 15% discount).
* **Audit Ledger**: Records every decision with timestamp, merchant, amount, reasoning, confidence, and realized monthly/annual savings.

---

## 6. Why This is Truly Agentic AI (Not Just a Classifier)

Judges often ask: *"Why is this an Agentic AI system rather than just a machine learning classifier?"*

| Typical ML Classifier | SpendGuardian Agentic AI |
| :--- | :--- |
| Only outputs a static label (e.g., `wasteful: 0.82`). | **Executes a closed-loop multi-step reasoning cycle**: Perceives environment → Gathers data → Reasons → Evaluates safety → Acts → Observes outcome. |
| Cannot take actions in the real world. | **Takes autonomous action**: Cancels mandates, updates database states, and logs savings to the ledger. |
| Blind to safety constraints and dollar limits. | **Has deterministic guardrails**: Enforces hard user limits and strictly protected category whitelists. |
| Cannot handle ambiguity or human collaboration. | **Human-in-the-loop escalation**: Knows when it is uncertain and escalates with clear plain-language rationale. |
| No negotiation or conversational capabilities. | **Negotiation Agent**: Generates retention pitch letters and negotiates discounts with merchants. |

---

## 7. Deterministic Guardrails: The Safety Core

Agentic autonomy without safety boundaries is dangerous. SpendGuardian implements deterministic guardrails:

1. **Autonomous Spending Ceiling (`auto_action_limit`)**:
   * Default: ₹2,000 / $20.
   * If a subscription costs more than this limit, the agent is **forbidden from auto-cancelling**, regardless of how inactive it is. It must escalate to the user.
2. **Strictly Protected Categories (`protected_categories`)**:
   * Default: `["insurance", "loan_payment", "healthcare", "utility", "education", "tax"]`.
   * Essential payments (e.g., HealthGuard Insurance or Home Loan EMI) may not have frequent user logins, but cancelling them could cause catastrophic life consequences. The guardrail engine **strictly blocks autonomy** on these categories with 100% certainty.
3. **Ambiguity & Duplicate Gate**:
   * If two competing services exist in the same category and both were used within 90 days (e.g., TuneWave used 4 days ago vs MusicBox used 40 days ago), the agent **refuses to guess user preference** and escalates for approval.
4. **Certainty Threshold (`min_confidence_threshold`)**:
   * If decision confidence drops below 85%, autonomy is blocked.

---

## 8. Sample Scenarios & Problem Statement Validation

The project includes built-in verification for the exact scenarios specified in the hackathon challenge:

### Scenario 1 — Clear waste, safe to act (INPUT 1)
* **Input**: User prompt *"Go through my subscriptions and clean up anything I'm not using."*
  * Merchant: `StreamFlix`
  * Amount: `₹649` ($14.99) / month
  * Inactivity: `187 days ago`
  * Guardrail: `auto_action_limit: ₹2,000` ($20)
* **Agent Behavior**:
  * Calculates Waste Score: `100/100` (Severe inactivity).
  * Confidence: `98%`.
  * Guardrail Check: Amount (₹649) is below ₹2,000 limit; not in protected category.
  * **Action**: `AUTO_CANCEL`.
  * **Result**: Mandate cancelled; logs *"Unused for 187 days. Monthly charge of ₹649 is well within your safety limit. Automatically cancelled to stop recurring leak."*

### Scenario 2 — Ambiguous, needs judgment (INPUT 2)
* **Input**: Overlapping subscriptions in `music_streaming`:
  * `TuneWave`: `₹399` ($9.99), used `4 days ago` (active).
  * `MusicBox Premium`: `₹499` ($11.99), used `40 days ago`.
* **Agent Behavior**:
  * Detects duplicate category: `music_streaming`.
  * Recognizes `TuneWave` is actively used and `MusicBox` is less active.
  * Recognizes that user preference cannot be assumed.
  * Lowers Confidence to `65%` (< 85% threshold).
  * **Action**: `ESCALATE_APPROVAL`.
  * **Result**: Does NOT auto-cancel. Displays side-by-side approval card: *"You currently pay for two music services. TuneWave was used 4 days ago, while MusicBox was last used 40 days ago. I recommend reviewing MusicBox, but will not cancel without your approval."*

### Scenario 3 — Guardrail blocks autonomy (INPUT 3)
* **Input**:
  * `HealthGuard Insurance`: `₹2,500` ($89.00) / month
  * Category: `insurance`
  * Inactivity: `210 days ago`
  * Guardrail: `protected_categories: ["insurance", "loan_payment"]`
* **Agent Behavior**:
  * Inspects category: `insurance`.
  * Category matches strictly protected whitelist.
  * **Action**: `BLOCKED_GUARDRAIL` → `ESCALATE_APPROVAL`.
  * **Result**: Autonomy strictly prohibited. Displays: *"HealthGuard Insurance belongs to protected category 'insurance'. Essential subscriptions are strictly protected from autonomous cancellation by safety guardrails."*

---

## 9. Bonus & Stretch Capabilities Implemented

1. **Retention Negotiation Mode**:
   * Instead of cancelling outright, users or the agent can trigger negotiation mode.
   * Generates a formal loyalty retention appeal to the merchant.
   * Simulates merchant response with a **15% discount offer**.
   * User can click **"Accept Offer"** to reduce monthly fees and realize savings immediately.
2. **Price-Hike Prediction**:
   * Analyzes historical billing trends to flag upcoming annual price increase risks before the next cycle hits.
3. **Bundle Redundancy Detection**:
   * Flags when standalone subscriptions (e.g. Spotify) are redundant because an active bundled service (e.g. YouTube Premium with YouTube Music) already covers the functionality.
4. **Executive Monthly Savings Report**:
   * Generates an executive summary of reviewed subscriptions, dollars saved, and pending approvals.
   * Includes one-click **Markdown Export (`.md`)** and **Print/PDF** generation.

---

## 10. Folder Structure & Code Organization

```
kmit_project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app, CORS, lifespan seeding
│   │   ├── config.py                  # Settings, limits, protected categories
│   │   ├── database.py                # SQLAlchemy engine & SQLite session
│   │   ├── models.py                  # Database tables (Users, Subscriptions, ActionLogs)
│   │   ├── schemas.py                 # Pydantic request/response validation
│   │   ├── data/
│   │   │   ├── transactions.csv       # 12-month transaction dataset
│   │   │   ├── emails.json            # Simulated billing & price hike emails
│   │   │   └── seed_data.py           # Database seeder
│   │   ├── agent/
│   │   │   ├── orchestrator.py        # Central Agent Brain & execution pipeline
│   │   │   ├── transaction_parser.py  # Ingestion & date-delta recurring cadence
│   │   │   ├── email_analyzer.py      # Natural language & email event parser
│   │   │   ├── waste_analyzer.py      # Multi-factor waste score (0-100)
│   │   │   ├── confidence_engine.py   # Certainty scoring (0-100%)
│   │   │   ├── guardrail_engine.py    # Policy enforcement & safety guardrails
│   │   │   ├── bundle_detector.py     # Bundle & redundant service analysis
│   │   │   ├── price_hike_detector.py # Price hike & predictive risk engine
│   │   │   ├── negotiation_agent.py   # Merchant negotiation engine
│   │   │   ├── action_executor.py     # Execution & immutable audit logging
│   │   │   └── llm_provider.py       # Dual-mode (Local NLP Engine + API support)
│   │   └── routes/
│   │       ├── audit.py               # POST /api/audit (Run agent pipeline)
│   │       ├── subscriptions.py       # GET/POST subscriptions & actions
│   │       ├── guardrails.py          # GET/PUT user guardrail limits
│   │       ├── savings.py             # GET savings metrics & report
│   │       ├── audit_logs.py          # GET audit log history
│   │       ├── transactions.py        # GET raw transactions
│   │       └── emails.py              # GET scanned emails
│   ├── tests/
│   │   ├── test_sample_inputs.py      # Tests for INPUT 1, INPUT 2, and INPUT 3
│   │   └── test_agent_pipeline.py     # In-memory end-to-end audit test
│   └── requirements.txt
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx                    # Master financial control dashboard
│       ├── index.css                  # Custom glows, fonts, and dark styling
│       ├── services/
│       │   └── api.js                 # Axios API connector
│       └── components/
│           ├── Navbar.jsx             # Top bar, live status, audit trigger
│           ├── SavingsSummaryCards.jsx# Realized & projected savings cards
│           ├── AgentTerminal.jsx      # Visual trace of live agent reasoning
│           ├── ApprovalsSection.jsx   # Human-in-the-loop pending cards
│           ├── SubscriptionCard.jsx   # Detailed subscription item card
│           ├── GuardrailsModal.jsx    # Guardrail policy configuration
│           ├── NegotiationModal.jsx   # Merchant discount dialogue
│           ├── AuditLogTimeline.jsx   # Immutable compliance audit log
│           ├── TransactionsTable.jsx  # Bank statement feed explorer
│           ├── EmailExplorer.jsx      # Scanned billing emails explorer
│           └── SavingsReportModal.jsx # Executive monthly report preview
├── start.sh                           # Unified one-click startup script
└── README.md                          # Comprehensive project documentation
```

---

## 11. How to Run, Test, and Demonstrate

### 🚀 Quick Start (One Command)
Run the unified startup script from the project root:
```bash
cd /home/srisanth/kmit_hack/kmit_project
./start.sh
```
This automatically:
1. Starts the FastAPI backend at `http://127.0.0.1:8000`
2. Starts the React Vite frontend at `http://127.0.0.1:5173`
3. Opens the interactive Financial Control Center in your browser.

---

### 🧪 Running Backend Unit Tests
To verify all problem statement scenarios and agent logic using `pytest`:
```bash
cd /home/srisanth/kmit_hack/kmit_project/backend
PYTHONPATH=. ./venv/bin/pytest -v
```
**Output:**
```
tests/test_agent_pipeline.py::test_full_agent_audit_pipeline PASSED
tests/test_sample_inputs.py::test_input_1_clear_waste_safe_to_act PASSED
tests/test_sample_inputs.py::test_input_2_ambiguous_overlapping_services PASSED
tests/test_sample_inputs.py::test_input_3_guardrail_blocks_protected_category PASSED
tests/test_sample_inputs.py::test_price_hike_detection PASSED
tests/test_sample_inputs.py::test_bundle_redundancy_detection PASSED

======================== 6 passed in 0.31s ========================
```

---

### 📖 Interactive Swagger API Documentation
With the backend running, visit:
👉 **`http://127.0.0.1:8000/docs`**

You can test every endpoint directly:
* `POST /api/audit` — Run full agentic audit.
* `GET /api/subscriptions` — Fetch monitored subscriptions.
* `GET /api/savings` — Fetch realized and projected savings metrics.
* `GET /api/savings/report` — View formatted executive monthly report.
* `GET /api/guardrails` — View or update safety guardrails.

---

### 🎬 Recommended 3-Minute Demo Walkthrough for Evaluators
1. **The Problem & Setup**: Open the dashboard at `http://127.0.0.1:5173`. Show the 4 savings cards displaying ₹0 realized savings before the audit.
2. **Execute Agent Audit**: Click **"Run Guardian Audit"**. Point to the **Agent Reasoning Terminal** as it visualizes each step in real time:
   * Scanning 45 transactions across 12 months.
   * Parsing billing emails and price hike notices.
   * Detecting monthly and weekly cadences.
   * Evaluating waste scores and checking guardrails.
3. **Show Safe Autonomy (INPUT 1)**: Show `StreamFlix` (unused for 187 days, ₹649/mo). It was automatically cancelled under the ₹2,000 auto limit, stopping recurring spend with high confidence (98%).
4. **Show Ambiguity & Human-in-the-Loop (INPUT 2)**: Open the **Approvals Tab**. Show `TuneWave` (used 4 days ago) vs `MusicBox` (used 40 days ago). Explain why the agent escalated rather than guessing user preference. Click **"Cancel & Save"** or **"Keep Service"** to demonstrate human-in-the-loop resolution.
5. **Show Safety Lock (INPUT 3)**: Show `HealthGuard Insurance` (₹2,500/mo, inactive 210 days). Point to the **Protected Category** badge and explain why autonomy was strictly blocked by safety guardrails.
6. **Show Negotiation Mode (Stretch Feature)**: Click **"Negotiate"** on an active subscription. View the AI-drafted retention pitch and simulated merchant 15% discount. Click **"Accept Offer"** and watch monthly savings update immediately.
7. **Show Audit Ledger & Report**: Click **"Audit Trail"** to show the immutable compliance timeline, then click **"Monthly Report"** to show the printable executive briefing.

---
*Built with ❤️ for PRAGYAAN 2.0 Hackathon by the KMIT Team.*
