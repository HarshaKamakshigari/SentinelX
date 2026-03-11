"""
SentinelX v3 — Agentic SOC (LangGraph + Gemini)
FastAPI entry point with Threat Intelligence Knowledge Base integration.
"""
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models.log_model import SecurityLog
from .core.router import compile_graph
from .core.case_store import save_incident, get_all_incidents, clear_incidents
from .threat_intel.loader import load_dataset, record_count
from . import config  # noqa: F401 — triggers .env load & validation

logger = logging.getLogger(__name__)

app = FastAPI(
    title="SentinelX",
    version="3.0.0",
    description="Agentic Security Operations Center powered by LangGraph + Gemini with Threat Intelligence enrichment",
)

# CORS — allow dashboard to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load threat intelligence knowledge base at startup
logger.info("Loading Threat Intelligence Knowledge Base...")
_ti_count = load_dataset(config.THREAT_INTEL_DATASET)
logger.info("Threat Intel KB ready: %d malware records indexed", _ti_count)

# Compile the LangGraph workflow once at startup
workflow = compile_graph()


@app.post("/ingest")
async def ingest_log(log: SecurityLog):
    """
    Ingest a security log and process it through the agentic pipeline.
    Flow: Orchestrator → Malware → Network → ThreatIntel → VT → Triage → Report
    """
    initial_state = {"log_data": log.model_dump()}

    try:
        result = workflow.invoke(initial_state)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {exc}")

    report = result.get("final_report", {"error": "No report generated"})

    # Persist for dashboard
    save_incident(report)

    return report


@app.get("/incidents")
async def list_incidents():
    """Return all stored incidents for the dashboard."""
    return get_all_incidents()


@app.delete("/incidents")
async def delete_incidents():
    """Clear all stored incidents."""
    clear_incidents()
    return {"status": "cleared"}


@app.get("/threat-intel/stats")
async def threat_intel_stats():
    """Return threat intelligence knowledge base statistics."""
    return {
        "records": record_count(),
        "source": "MalwareBazaar",
        "dataset": "malware_90ds_filtered.csv",
        "status": "loaded",
    }


@app.get("/")
async def root():
    return {
        "service": "SentinelX",
        "version": "3.0.0",
        "status": "operational",
        "engine": "LangGraph +  gemini 3-pro preview",
        "threat_intel": {
            "enabled": True,
            "source": "MalwareBazaar",
            "records": record_count(),
        },
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
