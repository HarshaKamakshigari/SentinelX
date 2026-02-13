We need to refactor the SentinelX LangGraph workflow to use TRUE conditional routing instead of sequential execution.

Current Problem:
The graph is sequential:
Orchestrator → Malware → Network → VT → Triage → Report

Each node internally skips execution using flags.
This is not true multi-agent conditional branching.

Goal:
Implement real conditional routing using LangGraph's add_conditional_edges.

Requirements:

1. Keep all existing agent nodes unchanged.
2. Modify compile_graph() to:

   - Entry point: orchestrator
   - From orchestrator, conditionally route to:
        - malware_agent (if invoke_malware == True)
        - network_agent (if invoke_network == True)
        - vt_agent (if invoke_vt == True)

3. After specialist agents complete, route to triage_agent.
4. Then route to report_agent.
5. Then END.

6. Use proper routing functions like:

   def route_from_orchestrator(state):
       return {
           "malware": state.get("invoke_malware", False),
           "network": state.get("invoke_network", False),
           "vt": state.get("invoke_vt", False)
       }

7. Use add_conditional_edges properly so that:
   - If flag is False → skip node entirely.
   - If True → execute that agent node.

8. Ensure that multiple agents can run in parallel (fan-out pattern),
   and after all selected agents complete, they converge into triage_agent.

9. Use LangGraph's support for parallel branches (fan-out, fan-in).

10. Keep SentinelState unchanged.

11. The final graph structure should logically look like:

        Orchestrator
              ↓
     ┌────────┼────────┐
     ↓        ↓        ↓
 Malware   Network     VT
     └────────┼────────┘
              ↓
           Triage
              ↓
           Report
              ↓
             END

12. Ensure graph.compile() returns compiled workflow.

13. Code must be clean, production-ready, and suitable for final year project demonstration.

Refactor only compile_graph() and add necessary routing helper functions.
Do not modify agent logic.
