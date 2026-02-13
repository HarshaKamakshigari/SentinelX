"""
SentinelX — Agentic SOC (LangGraph + Gemini)
FastAPI entry point.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models.log_model import SecurityLog
from .core.router import compile_graph
from .core.case_store import save_incident, get_all_incidents, clear_incidents
from . import config  # noqa: F401 — triggers .env load & validation

app = FastAPI(
    title="SentinelX",
    version="2.0.0",
    description="Agentic Security Operations Center powered by LangGraph + Gemini",
)

# CORS — allow dashboard to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compile the LangGraph workflow once at startup
workflow = compile_graph()


@app.post("/ingest")
async def ingest_log(log: SecurityLog):
    """
    Ingest a security log and process it through the agentic pipeline.
    Flow: Orchestrator → Specialist Agents → Triage → Report
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


@app.get("/")
async def root():
    return {
        "service": "SentinelX",
        "version": "2.0.0",
        "status": "operational",
        "engine": "LangGraph + Gemini 2.0 Flash",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
