Perfect. You’re building something serious now.

Below is a **clean, implementation-ready Product Requirements Document (PRD)** tailored for your **Agentic SOC – MVP**, designed so you can directly start building using **Langchain or langrapgh or both combined(MAS framework)** + Python stack.

---

# 🛡️ Product Requirements Document (PRD)

## Product Name: SentinelX (Agentic SOC – MVP)

---

# 1️⃣ Product Overview

## 🎯 Vision

Build a lightweight, cross-platform **Agentic Security Operations Center (SOC)** that:

* Dynamically routes security logs to specialized AI agents
* Performs automated triage, enrichment, and correlation
* Generates SOC-style incident reports
* Does NOT rely on SIEM platforms

---

## 🧠 Core Innovation (Paper Angle)

> Dynamic semantic-based agent routing + confidence-weighted incident reporting.

Not just tool calls — **decision intelligence orchestration.**

---

# 2️⃣ Problem Statement

Traditional SOCs:

* Require heavy SIEMs (e.g., Splunk)
* Are rule-heavy
* Lack dynamic reasoning
* Require manual triage

We want:

* Lightweight
* Cross-platform
* AI-native
* Autonomous triage

---

# 3️⃣ Target Users

| User Type           | Description                      |
| ------------------- | -------------------------------- |
| Security Researcher | Evaluating AI for SOC automation |
| University Lab      | Testing MAS security reasoning   |
| Small SOC Team      | Lightweight detection layer      |

---

# 4️⃣ Scope (MVP Only)

### ✅ Included

* Windows + macOS log ingestion
* 6-agent architecture
* Static + heuristic malware detection
* VirusTotal enrichment
* Network anomaly detection
* Incident report generation
* Case storage (SQLite)

### ❌ Not Included (Future)

* Real-time EDR
* Sandbox detonation
* Full SIEM replacement
* Cloud telemetry

---

# 5️⃣ High-Level Architecture

```
Log Collector
      ↓
Orchestrator Agent (Antigravity MAS)
      ↓
Specialized Agents
      ↓
Report Agent
      ↓
Incident Store (SQLite)
```

---

# 6️⃣ Functional Requirements

---

## FR-1: Log Ingestion

### Sources

| Log Type         | Platform | Method              |
| ---------------- | -------- | ------------------- |
| Process Creation | Windows  | Event ID 4688       |
| PowerShell Logs  | Windows  | ScriptBlock logging |
| Unified Logs     | macOS    | `log show`          |
| Network Logs     | Both     | osquery             |

### Implementation

* Python collector service
* Convert logs → normalized JSON

Example:

```json
{
  "host": "win-01",
  "event_type": "process_creation",
  "command_line": "powershell -enc ...",
  "hash": "abcd1234",
  "destination_ip": "45.77.12.90"
}
```

---

## FR-2: Orchestrator Agent (Brain)

### Responsibilities

* Classify event type
* Route to relevant agents
* Maintain case context
* Aggregate responses

### Routing Logic

Hybrid:

* Rule-based first
* LLM-based semantic fallback

Example:

```
IF command contains "-enc"
→ route to Malware Agent
→ route to VirusTotal Agent
```

---

## FR-3: Triage Agent

### Responsibilities

* Assign severity (LOW/MED/HIGH)
* Deduplicate similar events
* Produce confidence score

Output:

```json
{
  "severity": "HIGH",
  "confidence": 0.89,
  "reason": "Encoded PowerShell + external IP"
}
```

---

## FR-4: Malware Agent

### Responsibilities

* Detect:

  * Base64 PowerShell
  * rundll32 abuse
  * mshta execution
  * LOLBins

### Tools

* Regex engine
* YARA-lite rules
* Pattern database

No sandbox required for MVP.

---

## FR-5: VirusTotal Agent

### Responsibilities

* Hash lookup
* IP reputation lookup
* Domain reputation lookup

Uses:

* VirusTotal API

Output:

```json
{
  "vt_score": "18/70",
  "verdict": "malicious"
}
```

---

## FR-6: Network Agent

### Responsibilities

* Detect:

  * Rare ports
  * Suspicious outbound IPs
  * Geo mismatch
  * Known bad IP list

MVP:

* Static malicious IP dataset
* Basic anomaly detection

---

## FR-7: Report Agent

### Responsibilities

* Merge outputs
* Generate:

  * Incident summary
  * Timeline
  * MITRE mapping
  * Confidence score

Example:

```
Incident ID: SOC-2026-001
Severity: HIGH
MITRE: T1059.001, T1071
Confidence: 0.92
```

---

# 7️⃣ Non-Functional Requirements

| Requirement   | Description           |
| ------------- | --------------------- |
| Latency       | < 3 seconds per event |
| Scalability   | Modular agent design  |
| Extensibility | Plug-in agent model   |
| Storage       | SQLite                |
| API           | REST (FastAPI)        |

---

# 8️⃣ Tech Stack

## 🧠 Multi-Agent Framework

* Antigravity (Primary MAS framework)
* Alternative: LangGraph

---

## 🧩 Backend

* Python 3.11+
* FastAPI
* Uvicorn

---

## 🗃 Storage

* SQLite (MVP)
* JSON case store

---

## 🔎 Log Collection

### Windows

* winlogbeat (optional)
* Python + `wevtutil`

### macOS

* `log show`
* osquery

---

## 🧪 External APIs

* VirusTotal API

---

## 📦 Optional Enhancements

* Redis (queue)
* Dockerized agents
* MITRE mapping JSON
* Simple React dashboard

---

# 9️⃣ Data Model

## Case Schema

```json
{
  "case_id": "SOC-2026-001",
  "host": "win-01",
  "events": [],
  "agents_invoked": [],
  "severity": "HIGH",
  "confidence": 0.91,
  "mitre": [],
  "status": "open"
}
```

---

# 🔟 Milestone Plan (Build Order)

---

## Phase 1 – Core Skeleton (Week 1)

* Setup FastAPI
* Setup Antigravity
* Build Orchestrator agent
* Hardcoded log input
* Simple routing

---

## Phase 2 – Intelligence Layer (Week 2)

* Malware Agent
* VirusTotal Agent
* Triage Agent
* Case store (SQLite)

---

## Phase 3 – Network + Report (Week 3)

* Network Agent
* Report Agent
* MITRE mapping
* JSON → Markdown report

---

## Phase 4 – Demo Simulation

Simulate:

1. Encoded PowerShell
2. Malicious hash
3. Outbound IP

System should:

* Route correctly
* Correlate
* Generate report

This becomes:

* Demo
* Evaluation section
* Research validation

---

# 🔥 Architecture Decision Justification (For Paper)

| Decision            | Why                            |
| ------------------- | ------------------------------ |
| No SIEM             | Lightweight research prototype |
| MAS design          | Modular intelligence           |
| Confidence scoring  | Trust-aware automation         |
| External enrichment | Real-world validation          |
| SQLite              | MVP simplicity                 |

---

# 📊 Evaluation Plan (For Research Section)

Measure:

1. Detection Accuracy
2. Agent Routing Precision
3. False Positive Rate
4. Report Quality Score
5. Latency per event

---

# 🧠 Future Roadmap (After MVP)

* Reinforcement-learning routing
* Agent self-improvement memory
* Distributed agents
* Federated SOC
* Real-time streaming mode

---

# 🚀 Final Execution Strategy For You

Since you’re strong in:

* Cybersecurity
* Multi-agent systems
* Research writing
* Python

Build this as:

```
/sentinelx
    /agents
    /orchestrator
    /collectors
    /store
    /reports
```

Keep everything modular.

---
