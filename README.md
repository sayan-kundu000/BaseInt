# BaseInt: Enterprise SQL & Database Analytics Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-brightgreen.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy%202.0-red.svg)](https://www.sqlalchemy.org/)
[![Guardrails](https://img.shields.io/badge/Security-AST%20%2B%20NeMo-success.svg)](#ast-sql-safety-filter--guardrails)
[![Documentation PDF](https://img.shields.io/badge/Docs-37%20Pages%20PDF-purple.svg)](BaseInt_Documentation.pdf)
[![Portal](https://img.shields.io/badge/Localhost-Port%203000-blueviolet.svg)](http://localhost:3000)

**BaseInt** is an enterprise-grade autonomous SQL and Database Analytics Agent engineered with **LangGraph state machines**, dynamic **SQLAlchemy metadata reflection**, an **Abstract Syntax Tree (AST) safety filter** enforcing strict read-only execution, **NVIDIA NeMo Guardrails** input protection, and an interactive **Streamlit dashboard with dynamic Plotly charting canvases**.

- **Repository**: [https://github.com/sayan-kundu000/BaseInt](https://github.com/sayan-kundu000/BaseInt)
- **Localhost 3000 Portal**: [http://localhost:3000](http://localhost:3000)
- **Documentation PDF**: [BaseInt_Documentation.pdf](BaseInt_Documentation.pdf) (37 Topics, 37 Pages, 7 Paragraphs per Page)

---

## 1. System Architecture & Workflow

```
[ Natural Language Query ]
            │
            ▼
┌───────────────────────────────┐
│   NeMo Guardrails Input Rail  │ ──(Tautology / Comment / Script / DDL detected)──► [ Security Warning Alert ]
└───────────────────────────────┘
            │ (Pass)
            ▼
┌───────────────────────────────┐
│     inspect_schema_node       │ ◄─── SQLAlchemy Dynamic Metadata Introspection
└───────────────────────────────┘
            │
            ▼
┌───────────────────────────────┐
│       generate_sql_node       │ ◄─── Zero-Temp LLM / Heuristic Fallback
└───────────────────────────────┘
            │
            ▼
┌───────────────────────────────┐
│      execute_query_node       │
│  - AST Safety Filter Check    │ ──(Non-SELECT / DDL / DML detected)─────────────► [ Security Block Alert ]
│  - SQLAlchemy Engine Exec     │
└───────────────────────────────┘
            │
     ┌──────┴─────────────────────────────────┐
     │                                        │
 (DB Error & Retries < 3)                 (Success)
     ▼                                        ▼
┌───────────────────────────────┐    ┌─────────────────────────────────────────┐
│        reflection_node        │    │ Streamlit UI & Dynamic Plotly Canvas    │
│  - Parse error diagnostics    │    │  - Tabular Results Dataframe            │
│  - Increment retry_count      │    │  - Auto-Heuristic Trend / Donut Chart   │
│  - Synthesize correction ctx  │    │  - Collapsible Telemetry & Query Feeds  │
└───────────────────────────────┘    └─────────────────────────────────────────┘
     │
     └─────────► Loops back to generate_sql_node (Capped at 3 retries)
```

---

## 2. Core Functional Highlights

### 2.1 LangGraph SQL Generation Graph with Reflection Loop
- **State Machine**: Tracks `user_query`, `generated_sql`, `db_result`, `error_message`, and `retry_count`.
- **`inspect_schema_node`**: Introspects table structures, column types, primary keys, and foreign keys via SQLAlchemy at runtime.
- **`generate_sql_node`**: Generates optimal, dialect-aware read-only SQL queries with zero temperature.
- **`execute_query_node`**: Runs queries against SQLite or PostgreSQL backends, capturing duration telemetry and catching operational errors.
- **`reflection_node`**: Intercepts database exceptions (e.g. `no such column`), increments the retry counter, diagnoses the missing schema entity, and routes back to the generator with targeted correction instructions.
- **3-Retry Threshold**: Self-correction is strictly capped at a maximum of 3 retries, guaranteeing bounded termination.

### 2.2 AST SQL Safety Filter & NeMo Guardrails
- **AST Pre-Execution Validation**: Implements Abstract Syntax Tree analysis using `sqlparse` and `sqlglot` via `is_safe_select_only()`. Explicitly blocks write and modification operations (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`), allowing solely pure `SELECT` queries.
- **Multi-Statement Blocking**: Rejects chained semicolon queries (`SELECT ...; DROP TABLE ...;`).
- **NeMo Guardrails Input Scanner**: Sanitizes raw input queries prior to LLM processing:
  - Blocks tautology exploits (`1=1`, `'a'='a'`, `orders' OR '1'='1'`).
  - Blocks comment expansion tricks (`--`, `/* ... */`, `#`).
  - Blocks Cross-Site Scripting (XSS) and script injection (`<script>`, `javascript:`, `<iframe>`).
  - Rejects explicit destructive phrases before token submission.

### 2.3 Streamlit Dashboard with Dynamic Plotly Visuals
- **Query Input Panel**: Natural language prompt field with 5 quick-test preset buttons.
- **Code & Log Feeds**: Collapsible `st.expander` windows displaying generated SQL, runtime telemetry, latency metrics, and reflection histories.
- **Plotly Visual Heuristics**: Automatically inspects returned dataframes:
  - *Time-series columns* $\rightarrow$ Interactive Line Charts with date markers.
  - *Low-cardinality categories ($\le 7$)* $\rightarrow$ Interactive Donut Charts.
  - *High-cardinality categories ($> 7$)* $\rightarrow$ Sorted Horizontal/Vertical Bar Charts.
- **Localhost 3000 Links**: Embedded navigation pills linking directly to [http://localhost:3000](http://localhost:3000).

---

## 3. Installation & Quickstart

### 3.1 Clone & Setup Environment
```bash
git clone https://github.com/sayan-kundu000/BaseInt.git
cd BaseInt

# Create and activate virtual environment (optional)
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux / macOS

# Install dependencies
pip install -r requirements.txt
```

### 3.2 Configure Environment
```bash
cp .env.example .env
```
Edit `.env` to configure your settings (SQLite database is configured by default; set `OPENAI_API_KEY` for live model generation):
```env
DATABASE_URL=sqlite:///./baseint_analytics.db
OPENAI_API_KEY=your_key_here  # Optional: Fallback deterministic engine runs offline
MAX_RETRIES=3
STREAMLIT_SERVER_PORT=8501
DOCS_SERVER_PORT=3000
BASE_URL=http://localhost:3000
```

### 3.3 Seed Sample Database
```bash
python scripts/seed_db.py
```
Populates `orders`, `customers`, `products`, and `order_items` tables with realistic business data.

### 3.4 Launch Streamlit Analytics Dashboard
```bash
streamlit run app.py
```
Open your browser at **`http://localhost:8501`**.

### 3.5 Launch Localhost 3000 Portal & Documentation Server
```bash
python server.py
```
Open **`http://localhost:3000`** to browse the 37 technical topics, check system health (`/api/v1/health`), and view security compliance tables.

---

## 4. Verification & Validation Test Cases

Grading and security compliance reviews execute the following exact workflows:

### Test Case 1: SQL Self-Correction Column-Reference Recovery Loop
1. Launch dashboard: `streamlit run app.py`.
2. Enter natural language prompt: `'Show orders sorted by date'` (or check *"Simulate initial column error"*).
3. The model attempts to query the non-existent column `created_at`.
4. The execution node catches database error: `no such column: created_at`.
5. The reflection node captures the error, diagnoses available schema columns, and prompts the generator.
6. The generator rewrites the SQL using `order_date`:
   ```sql
   SELECT id, order_date, customer_id, amount, status FROM orders ORDER BY order_date DESC;
   ```
7. Results execute successfully and render on the Plotly timeline canvas.

### Test Case 2: AST Safety Filter & SQL Injection Block
1. Input adversarial payload: `'DROP TABLE orders; --'`
2. NeMo Guardrails and AST parser intercept the malicious command prior to database execution.
3. A security warning alert is rendered: *"AST Validation Rejected: Operation DROP is prohibited."*
4. No queries are transmitted to the database, and table `orders` remains 100% intact with all 30 records preserved.

### Test Case 3: Automated Test Suite Execution
Run the complete automated pytest suite:
```bash
pytest -v
```
**Result**: 16/16 tests pass with 0 failures and 0 warnings:
```
tests/test_ast_guardrails.py::test_ast_allows_valid_select_queries PASSED
tests/test_ast_guardrails.py::test_ast_rejects_delete_statements PASSED
tests/test_ast_guardrails.py::test_ast_rejects_drop_statements PASSED
tests/test_ast_guardrails.py::test_ast_rejects_insert_and_update_statements PASSED
tests/test_ast_guardrails.py::test_ast_rejects_multi_statement_injections PASSED
tests/test_nemo_guardrails.py::test_nemo_allows_safe_queries PASSED
tests/test_nemo_guardrails.py::test_nemo_blocks_destructive_commands PASSED
tests/test_nemo_guardrails.py::test_nemo_blocks_tautologies PASSED
tests/test_nemo_guardrails.py::test_nemo_blocks_script_injection PASSED
tests/test_query_executor.py::test_execute_query_node_success PASSED
tests/test_query_executor.py::test_execute_query_node_catches_db_error PASSED
tests/test_reflection_loop.py::test_reflection_loop_recovers_from_invalid_column PASSED
tests/test_reflection_loop.py::test_ast_and_nemo_prevent_drop_table_without_modifying_db PASSED
tests/test_reflection_loop.py::test_reflection_retry_cap_at_three PASSED
tests/test_schema_inspector.py::test_schema_reflection_discovers_all_tables PASSED
tests/test_schema_inspector.py::test_format_schema_for_prompt PASSED
```

---

## 5. Technical Documentation Manual (37 Topics / 37 Pages)

BaseInt includes a publication-grade, 37-page architectural reference manual compiled via ReportLab Platypus into **`BaseInt_Documentation.pdf`**. Each topic is formatted across exactly one page with exactly 7 medium-sized paragraphs and explicit links to **`http://localhost:3000`**.

| Topic # | Title | Localhost 3000 Link |
| :---: | :--- | :--- |
| **1** | High-Level Architecture of BaseInt & Production Agentic Analytics | [localhost:3000/docs/topic-1](http://localhost:3000/docs/topic-1) |
| **2** | Full Technology Stack Deep-Dive: Python, LangGraph, SQLAlchemy & NeMo | [localhost:3000/docs/topic-2](http://localhost:3000/docs/topic-2) |
| **3** | Relational Database Operations & Text-to-SQL Enterprise Challenges | [localhost:3000/docs/topic-3](http://localhost:3000/docs/topic-3) |
| **4** | SQLAlchemy Metadata Introspection & Dynamic Schema Reflection | [localhost:3000/docs/topic-4](http://localhost:3000/docs/topic-4) |
| **5** | Schema Representation Formatting & LLM Context Optimization | [localhost:3000/docs/topic-5](http://localhost:3000/docs/topic-5) |
| **6** | LangGraph State Machine Architecture & State Dictionary Design | [localhost:3000/docs/topic-6](http://localhost:3000/docs/topic-6) |
| **7** | Node Coordination & Deterministic State Transitions in LangGraph | [localhost:3000/docs/topic-7](http://localhost:3000/docs/topic-7) |
| **8** | LLM SQL Generation Node: Few-Shot Prompting & Temperature Control | [localhost:3000/docs/topic-8](http://localhost:3000/docs/topic-8) |
| **9** | Query Execution Engine: Engine Pooling & Exception Handling | [localhost:3000/docs/topic-9](http://localhost:3000/docs/topic-9) |
| **10** | Database Error Reflection Loop: Recovery from Column Hallucinations | [localhost:3000/docs/topic-10](http://localhost:3000/docs/topic-10) |
| **11** | Self-Correction Convergence & 3-Retry Threshold Capping | [localhost:3000/docs/topic-11](http://localhost:3000/docs/topic-11) |
| **12** | Abstract Syntax Tree (AST) Validation Principles with sqlparse | [localhost:3000/docs/topic-12](http://localhost:3000/docs/topic-12) |
| **13** | Multi-Statement Injection Prevention & Dialect-Aware Tokenization | [localhost:3000/docs/topic-13](http://localhost:3000/docs/topic-13) |
| **14** | Defense-in-Depth: Blocking DDL and DML Write Operations | [localhost:3000/docs/topic-14](http://localhost:3000/docs/topic-14) |
| **15** | NeMo Guardrails Integration: Input Rail Pattern Filtering | [localhost:3000/docs/topic-15](http://localhost:3000/docs/topic-15) |
| **16** | Defeating SQL Injection: Tautology Exploit Mitigation Strategies | [localhost:3000/docs/topic-16](http://localhost:3000/docs/topic-16) |
| **17** | Comment Expansion Attacks & Sanitization of Escape Sequences | [localhost:3000/docs/topic-17](http://localhost:3000/docs/topic-17) |
| **18** | Script Tag Sanitization & Cross-Site Scripting (XSS) Prevention | [localhost:3000/docs/topic-18](http://localhost:3000/docs/topic-18) |
| **19** | Streamlit Dashboard Architecture & State Synchronization | [localhost:3000/docs/topic-19](http://localhost:3000/docs/topic-19) |
| **20** | Collapsible Query Code, Telemetry Feeds & Execution Tracing | [localhost:3000/docs/topic-20](http://localhost:3000/docs/topic-20) |
| **21** | Dynamic Plotly Chart Canvas: Automated Visual Heuristics | [localhost:3000/docs/topic-21](http://localhost:3000/docs/topic-21) |
| **22** | Time Series Analysis & Temporal Aggregations in Business Intelligence | [localhost:3000/docs/topic-22](http://localhost:3000/docs/topic-22) |
| **23** | Categorical Breakdown Heuristics: Donut vs. Bar Chart Rules | [localhost:3000/docs/topic-23](http://localhost:3000/docs/topic-23) |
| **24** | Automated Unit & Security Testing Suite Design with Pytest | [localhost:3000/docs/topic-24](http://localhost:3000/docs/topic-24) |
| **25** | Verification Workflow 1: Column-Reference Recovery Loop | [localhost:3000/docs/topic-25](http://localhost:3000/docs/topic-25) |
| **26** | Verification Workflow 2: AST Safety Filter & SQL Injection Block | [localhost:3000/docs/topic-26](http://localhost:3000/docs/topic-26) |
| **27** | Secrets Isolation, Environment Variables & Configuration Hygiene | [localhost:3000/docs/topic-27](http://localhost:3000/docs/topic-27) |
| **28** | Monorepo Organization, Packaging & Modular Software Design | [localhost:3000/docs/topic-28](http://localhost:3000/docs/topic-28) |
| **29** | PostgreSQL vs. SQLite Adaptation: Concurrency & Transaction Isolation | [localhost:3000/docs/topic-29](http://localhost:3000/docs/topic-29) |
| **30** | Enterprise RBAC, Column-Level Masking & Data Governance | [localhost:3000/docs/topic-30](http://localhost:3000/docs/topic-30) |
| **31** | Production Observability, OpenTelemetry & Latency Budgets | [localhost:3000/docs/topic-31](http://localhost:3000/docs/topic-31) |
| **32** | Caching Strategies: Semantic Query Cache & Schema Caching | [localhost:3000/docs/topic-32](http://localhost:3000/docs/topic-32) |
| **33** | Scalability & Horizontal Deployment: Docker, Kubernetes & Workers | [localhost:3000/docs/topic-33](http://localhost:3000/docs/topic-33) |
| **34** | Industry Use Case: Financial Fraud Detection & Audit Compliance | [localhost:3000/docs/topic-34](http://localhost:3000/docs/topic-34) |
| **35** | Industry Use Case: E-Commerce Inventory Optimization & Fulfillment | [localhost:3000/docs/topic-35](http://localhost:3000/docs/topic-35) |
| **36** | Industry Use Case: SaaS Product Analytics & Churn Prediction | [localhost:3000/docs/topic-36](http://localhost:3000/docs/topic-36) |
| **37** | Future Horizons: Natural Language Data Meshes & Multi-Agent Swarms | [localhost:3000/docs/topic-37](http://localhost:3000/docs/topic-37) |

To recompile the documentation PDF:
```bash
python scripts/build_docs.py
```

---

## 6. Project Layout

```
BaseInt/
├── app/
│   ├── __init__.py
│   ├── config.py                 # Pydantic v2 settings & environment manager
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py              # LangGraph StateGraph with reflection loops
│   │   ├── nodes.py              # Schema inspection, generation, execution, reflection nodes
│   │   ├── prompts.py            # System prompts & reflection error correction templates
│   │   └── state.py              # Strongly-typed AgentState dictionary
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py         # SQLAlchemy engine & session factory
│   │   ├── schema.py             # Schema reflection & prompt formatting
│   │   └── seed.py               # Database schema definitions & seeding
│   ├── guardrails/
│   │   ├── __init__.py
│   │   ├── ast_filter.py         # Abstract Syntax Tree parser (sqlparse & sqlglot)
│   │   └── nemo_filter.py        # NeMo input guardrails (tautology, comment, XSS filters)
│   └── ui/
│       ├── __init__.py
│       ├── charts.py             # Plotly automated visual heuristics
│       └── dashboard.py          # Interactive Streamlit UI
├── configs/
│   └── guardrails/
│       ├── config.yml            # NeMo Guardrails configuration manifest
│       └── rails.co              # Colang input safety flows
├── docs/
│   ├── README.md                 # Documentation table of contents
│   ├── BaseInt_Documentation.pdf # 37-page compiled technical manual
│   └── topics/                   # 37 Markdown topic files (7 paragraphs each)
├── scripts/
│   ├── build_docs.py             # PDF documentation compiler
│   └── seed_db.py                # Database seeding CLI
├── tests/
│   ├── conftest.py               # In-memory test fixtures
│   ├── test_ast_guardrails.py    # AST write rejection assertions
│   ├── test_nemo_guardrails.py   # NeMo input pattern checks
│   ├── test_query_executor.py    # Cursor execution & telemetry tests
│   ├── test_reflection_loop.py   # Test Case 1 & 2 recovery assertions
│   └── test_schema_inspector.py  # SQLAlchemy metadata reflection checks
├── app.py                        # Streamlit dashboard entrypoint
├── server.py                     # Localhost 3000 portal & documentation server
├── .env.example                  # Environment configuration template
├── .gitignore                    # Secrets & cache exclusions
├── BaseInt_Documentation.pdf     # Root copy of 37-page PDF manual
├── requirements.txt              # Pinned Python dependencies
└── README.md                     # Comprehensive project documentation
```

---

## 7. License & Credits

Developed by **Sayan Sunil Kumar Rita Kundu** ([@sayan-kundu000](https://github.com/sayan-kundu000)).  
Licensed under the [MIT License](LICENSE).
