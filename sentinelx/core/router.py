"""
LangGraph Workflow — Compiles the SentinelX agent graph.

Flow (Sequential with conditional skipping):
  Input → Orchestrator → Malware → Network → VT → Triage → Report → END

Each specialist agent checks the routing flags set by the Orchestrator
and skips processing if not invoked.
"""
from langgraph.graph import StateGraph, END
from ..models.state import SentinelState
from ..agents.orchestrator import orchestrator_node
from ..agents.malware_agent import malware_node
from ..agents.network_agent import network_node
from ..agents.vt_agent import vt_node
from ..agents.triage_agent import triage_node
from ..agents.report_agent import report_node


def compile_graph():
    """Build and compile the SentinelX LangGraph workflow."""

    graph = StateGraph(SentinelState)

    # --- Add nodes ---
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("malware_agent", malware_node)
    graph.add_node("network_agent", network_node)
    graph.add_node("vt_agent", vt_node)
    graph.add_node("triage_agent", triage_node)
    graph.add_node("report_agent", report_node)

    # --- Sequential edges (each agent checks its own flag) ---
    graph.set_entry_point("orchestrator")
    graph.add_edge("orchestrator", "malware_agent")
    graph.add_edge("malware_agent", "network_agent")
    graph.add_edge("network_agent", "vt_agent")
    graph.add_edge("vt_agent", "triage_agent")
    graph.add_edge("triage_agent", "report_agent")
    graph.add_edge("report_agent", END)

    return graph.compile()
