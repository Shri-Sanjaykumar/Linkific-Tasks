# Day 24: Production Readiness, Testing, Logging, Docker, Environment Variables & Monitoring

**Project:** Linkific Enterprise AI & Workflow Automation Service  
**Organization:** Linkific ([https://www.linkific.in/](https://www.linkific.in/))  
**Milestone:** Day 24 — Production Engineering & Microservice Hardening  
**Status:** **62/62 AUTOMATED TESTS PASSED (90% COVERAGE) — STAGED FOR PRODUCTION**  

---

## 🎯 Learning Objectives Covered

- **Pytest:** Structured unit, API, integration, and cross-day regression test suites (62 tests, 100% pass rate) with fixtures, parameterization, and isolated subprocess execution.
- **Logging:** Production JSON-formatted structured logging with thread-safe `X-Correlation-ID` context propagation, rotating audit file handlers, and secret masking.
- **Docker Basics:** Security-hardened multi-stage `Dockerfile`, unprivileged non-root user execution (`appuser` UID 10001), `.dockerignore` hygiene, healthcheck probes, and `docker-compose.yml` orchestration with Prometheus.
- **Environment Variables:** Strongly-typed configuration management using `pydantic-settings` (`Settings`), `.env.example` documentation, validation constraints, default-key rejection in production, and runtime safety checks.
- **Monitoring:** Live OpenMetrics/Prometheus telemetry on `/metrics`, dual liveness (`/health/live`) and readiness (`/health/ready`) probes, sliding-window rate limiting (`RATE_LIMIT_PER_MINUTE=120`), and microsecond latency headers.

---

## 🏢 Linkific Company Project Practical

Linkific ([https://www.linkific.in/](https://www.linkific.in/)) provides **custom automation for finance teams**, removing tedious, repetitive tasks (such as invoice review, PO matching, approval routing, and policy compliance).

In Day 24, the company platform has been hardened into an enterprise microservice:
1. **Finance Automation API (`/api/v1/finance/invoice-approval`):** Evaluates vendor invoices against purchase orders, applying Straight-Through Processing (STP) for matches $\le \$1,000$, and escalating to Manager or Director tiers.
2. **Multi-Agent Research Assistant (`/api/v1/workflow/run`):** LangGraph StateGraph engine delivering factual corporate intelligence briefs with decimal-safe policy guarantees (`1.5 paid leave days`, `$500 hardware budget`, `80% test gate`).
3. **Structured Audit Logs:** Every financial and agent decision records an immutable audit entry into `data/service.log`.

---

## 📂 Project Structure

```
Day-24/
├── .env.example                     # Production environment variable template
├── .env                             # Local active configuration (ignored by Git)
├── .gitignore                       # Explicit Git ignore rules for secrets and caches
├── .dockerignore                    # Excludes build caches, secrets, and test artifacts
├── Dockerfile                       # Hardened multi-stage Docker build
├── docker-compose.yml               # Service & Prometheus orchestration
├── requirements.txt                 # Frozen production & testing dependencies
├── run_service.py                   # Local service bootstrap launcher
├── DEPLOYMENT_CHECKLIST.md          # Formal 7-pillar deployment verification checklist
├── PRODUCTION_READINESS_REPORT.md   # Exhaustive audit & readiness report
├── README.md                        # Primary technical documentation
├── app/
│   ├── __init__.py                  # Application package initialization
│   ├── main.py                      # FastAPI app factory, middleware & endpoints
│   ├── schemas.py                   # Pydantic v2 data models & request/response contracts
│   ├── state.py                     # LangGraph MultiAgentState & functional reducers
│   ├── graph.py                     # StateGraph engine with conditional routers
│   ├── core/
│   │   ├── __init__.py              # Core package export
│   │   ├── config.py                # Pydantic Settings environment configuration
│   │   ├── logging_config.py        # JSON structured logging & correlation context
│   │   └── metrics.py               # Prometheus metrics registry & formatting
│   └── nodes/
│       ├── __init__.py              # Node exports
│       ├── coordinator.py           # Planning & milestone egress node
│       ├── researcher.py            # Evidence retrieval & grounding node
│       ├── analyzer.py              # Cognitive clustering & synthesis node
│       ├── critic.py                # Adversarial audit & quality gate node
│       ├── writer.py                # Executive briefing & citation matrix node
│       └── error_handler.py         # Circuit breaker & failure mitigation node
├── data/
│   ├── company_docs.json            # Grounded enterprise policy corpus (9 policies)
│   └── service.log                  # Persistent rotating audit log
├── docs/
│   ├── DEPLOYMENT_CHECKLIST.md      # Mirror of deployment checklist
│   └── PRODUCTION_READINESS_REPORT.md # Mirror of production readiness report
└── tests/
    ├── __init__.py                  # Test suite init
    ├── conftest.py                  # PyTest fixtures & test client setup
    ├── test_regression.py           # Days 17, 20, 21, 22, and 23 backwards compatibility
    ├── unit/
    │   ├── test_config.py           # Configuration & environment variable tests
    │   ├── test_logging.py          # JSON logging & correlation ID tests
    │   ├── test_metrics.py          # Prometheus registry & telemetry tests
    │   ├── test_workflow_unit.py    # Agent reasoning node & graph tests
    │   └── test_finance_rules.py    # PO matching & invoice threshold unit tests
    └── api/
        ├── test_health_and_monitoring.py # Liveness, readiness, and metrics tests
        ├── test_auth_and_security.py     # API key gating & strict CORS tests
        ├── test_workflow_api.py          # Multi-agent HTTP execution tests
        ├── test_finance_api.py           # Finance automation API tests
        └── test_error_handling_api.py    # 404, 422, rate limiting & tracing header tests
```

---

## ⚙️ Environment Variables Reference

Copy `.env.example` to `.env` to configure the service:

| Variable | Type | Default | Description |
| :--- | :---: | :---: | :--- |
| `APP_NAME` | `str` | `Linkific Enterprise Automation Service` | Application identity string |
| `APP_VERSION` | `str` | `1.0.0` | Semantic version |
| `ENVIRONMENT` | `str` | `development` | Runtime mode: `development`, `staging`, `production`, `test` |
| `DEBUG` | `bool` | `false` | Enables hot reloading and debug diagnostics |
| `HOST` | `str` | `0.0.0.0` | Network binding interface |
| `PORT` | `int` | `8000` | Network binding port (1-65535) |
| `API_KEY` | `str` | *(Configured via .env)* | High-entropy authentication key required in `X-API-Key` header |
| `CORS_ORIGINS` | `list` | `["https://www.linkific.in","https://app.linkific.in","http://localhost:3000"]` | Allowed CORS origins for browser applications (wildcards stripped) |
| `LOG_LEVEL` | `str` | `INFO` | Logging threshold (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `LOG_FORMAT` | `str` | `json` | Formatting layout: `json` (production) or `text` (terminal) |
| `LOG_FILE_PATH` | `str` | `data/service.log` | Destination path for rotating log entries |
| `METRICS_ENABLED` | `bool` | `true` | Exposes Prometheus telemetry on `/metrics` |
| `RATE_LIMIT_PER_MINUTE` | `int` | `120` | Max requests per minute per client IP (HTTP 429 enforcement) |
| `MAX_WORKFLOW_REVISIONS` | `int` | `2` | Circuit breaker limit on adversarial agent revisions |

---

## 🚀 How to Run

### 1. Local Environment Execution
```powershell
# Navigate to Day-24 directory
cd C:\projects\linkific\internship\Day-24

# Install dependencies
pip install -r requirements.txt

# Start the service
python run_service.py
```
Service endpoints will be live at:
- **Interactive Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Liveness Probe:** [http://localhost:8000/health/live](http://localhost:8000/health/live)
- **Readiness Probe:** [http://localhost:8000/health/ready](http://localhost:8000/health/ready)
- **Prometheus Metrics:** [http://localhost:8000/metrics](http://localhost:8000/metrics)

---

### 2. Running Automated Tests with PyTest
```powershell
# Run the entire test suite (unit + api + regression)
python -m pytest -v

# Run only unit tests
python -m pytest tests/unit/ -v

# Run only API endpoint tests
python -m pytest tests/api/ -v

# Run cross-day regression tests
python -m pytest tests/test_regression.py -v
```

---

### 3. Docker Containerization & Orchestration

#### Build and Run Standalone Container
```bash
# Build production multi-stage image
docker build -t linkific-service:1.0.0 .

# Run container with environment configuration
docker run -d \
  --name linkific-app \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  linkific-service:1.0.0
```

#### Run with Docker Compose (Service + Prometheus Monitoring)
```bash
# Launch service and Prometheus scrape daemon
docker-compose up -d --build

# View container logs
docker-compose logs -f linkific-api

# Check healthcheck status
docker-compose ps

# Access Prometheus dashboard
open http://localhost:9090
```

---

## 📡 API Usage Examples (cURL)

### 1. Liveness & Readiness Probes
```bash
curl -X GET http://localhost:8000/health/live
curl -X GET http://localhost:8000/health/ready
```

### 2. Prometheus Metrics Scrape
```bash
curl -X GET http://localhost:8000/metrics
```

### 3. Finance Automation: Invoice Approval
```bash
curl -X POST http://localhost:8000/api/v1/finance/invoice-approval \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_CONFIGURED_API_KEY" \
  -d '{
    "invoice_id": "INV-2026-001",
    "po_number": "PO-8812",
    "vendor_name": "SaaS Cloud Technologies",
    "amount": 750.00,
    "currency": "USD"
  }'
```

### 4. Multi-Agent Intelligence Workflow
```bash
curl -X POST http://localhost:8000/api/v1/workflow/run \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_CONFIGURED_API_KEY" \
  -d '{
    "query": "What are the corporate guidelines regarding remote work, hardware allowances, and core collaboration hours?",
    "mode": "streamlined"
  }'
```

---

## 📊 Test Results Summary

```text
============================= 62 passed in 0.82s =============================
```
- **Unit Tests:** 36 passed (Configuration, Logging, Metrics, Agent Reasoning Nodes, Finance Approval Rules).
- **API Tests:** 21 passed (Liveness, Readiness, Prometheus Metrics, API Key Authentication, Strict CORS, Workflow, Finance Automation, Error Handling, Tracing Headers).
- **Regression Tests:** 5 passed (Days 17, 20, 21, 22, and 23 full cross-day backwards compatibility).
- **Branch-Aware Coverage:** 90%
- **Pass Rate:** 100% (62/62 tests passing).
