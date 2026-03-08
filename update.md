Overview

SentinelX v3 is an Agentic Security Operations Center (SOC) system that analyzes security logs using a multi-agent architecture powered by LangGraph and LLM reasoning.

The system ingests security telemetry, performs automated analysis through specialized agents, enriches findings with threat intelligence knowledge bases, and produces structured incident reports.

The goal of this upgrade is to make SentinelX:

Research-grade

production-ready

capable of real threat intelligence enrichment

evaluated on real malware datasets

Objectives
Primary Goals

Introduce a Threat Intelligence Knowledge Base built from malware datasets.

Add a Threat Intelligence Agent for malware family enrichment.

Integrate real-world malware indicators from a dataset.

Support offline hash intelligence lookup before external APIs.

Maintain modular agentic architecture using LangGraph.

Secondary Goals

Enable future integration with additional threat intel feeds.

Support similarity-based malware analysis.

Prepare the system for evaluation on real security datasets.

System Architecture
High Level Flow
Security Log
    ↓
Orchestrator Agent
    ↓
Malware Agent
    ↓
Network Agent
    ↓
Threat Intel Agent
    ↓
VirusTotal Agent
    ↓
Triage Agent
    ↓
Report Agent

Each agent reads and writes to a shared LangGraph state object.

Data Sources

The system uses a curated malware dataset derived from the MalwareBazaar database.

Dataset location:

data/malware_bazaar/malware_90ds_filtered.csv

Dataset columns:

date
sha256_hash
md5_hash
sha1_hash
reporter
file_name
file_type_guess
mime_type
signature
clamav
vtpercent
imphash
ssdeep
tlsh
Threat Intelligence Knowledge Base

A local threat intelligence index must be built from the dataset.

Required fields
sha256_hash
file_name
file_type_guess
mime_type
signature
vtpercent
ssdeep
tlsh
Knowledge Base Responsibilities

The KB should support:

hash lookup

malware family identification

detection confidence

similarity hashes (future use)

Expected Structure
data/
  malware_bazaar/
      malware_90ds_filtered.csv

sentinelx/
  threat_intel/
      loader.py
      index.py
Threat Intelligence Loader

A module must load the malware dataset at application startup.

Responsibilities:

parse CSV

build in-memory lookup table

map sha256_hash → malware metadata

Example record:

{
  "sha256": "...",
  "malware_family": "XWorm",
  "file_name": "123.exe",
  "file_type": "exe",
  "mime_type": "application/x-dosexec",
  "vt_percent": 40.5
}
Threat Intelligence Agent

A new LangGraph node must be added.

Responsibilities

check if a file hash exists in the threat intelligence KB

return malware classification

enrich the analysis state

Input
file_hash
Output
{
  threat_match: true/false,
  malware_family: string,
  file_name: string,
  file_type: string,
  vt_percent: float,
  source: "MalwareBazaar"
}

If no match is found:

{
  threat_match: false
}
Updated LangGraph State

The shared state must include new fields.

log_data

invoke_malware
invoke_network
invoke_vt
invoke_threatintel

malware_output
network_output
vt_output
threatintel_output

severity
confidence
triage_reason

final_report
Orchestrator Update

The orchestrator must now detect if a file hash exists and enable the Threat Intelligence agent.

Routing logic:

if file_hash exists:
    invoke_threatintel = true
Agent Execution Order

Update the LangGraph workflow.

orchestrator
    ↓
malware_agent
    ↓
network_agent
    ↓
threatintel_agent
    ↓
vt_agent
    ↓
triage_agent
    ↓
report_agent
Triage Agent Update

The triage agent must incorporate threat intelligence results.

Additional considerations:

known malware family

VT detection percentage

file type risk

Example reasoning:

Hash matched malware family XWorm
High VT detection rate
Confidence increased
Report Agent Update

The final report must include threat intelligence enrichment.

New fields in the report:

threat_intelligence:
    malware_family
    file_name
    file_type
    vt_percent
    source

Example report section:

Threat Intelligence:
Malware Family: XWorm
File Type: Windows Executable
Detection Rate: 40%
Source: MalwareBazaar
Performance Requirements

The system must:

load the dataset at startup

support instant hash lookups

process incidents in under 2 seconds

Security Requirements

no execution of downloaded malware

dataset must be treated as indicator metadata only

sanitize all inputs

Project Directory Structure

Expected structure:

sentinelx/

agents/
    malware_agent.py
    network_agent.py
    vt_agent.py
    threatintel_agent.py
    triage_agent.py
    report_agent.py
    orchestrator.py

core/
    router.py
    case_store.py

threat_intel/
    loader.py
    index.py

models/
    state.py
    log_model.py
    incident_model.py

data/
    malware_bazaar/
        malware_90ds_filtered.csv
Future Enhancements

The architecture should allow easy addition of:

MITRE ATT&CK knowledge base

anomaly detection agent

network reputation feeds

streaming log ingestion

persistent storage (PostgreSQL)

Deliverables

Cursor should implement:

Threat intelligence dataset loader

In-memory malware hash index

Threat Intelligence Agent

Updated LangGraph workflow

Updated state model

Updated incident report schema

Success Criteria

The upgraded system must:

correctly identify malware hashes present in the dataset

enrich incident reports with malware family information

maintain existing agent workflow

support real-world threat intelligence enrichment