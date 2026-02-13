We are upgrading the SentinelX project into a proper LangGraph-based multi-agent SOC system using Gemini API.

Requirements:

1. Use LangGraph StateGraph for orchestration.
2. Use LangChain + langchain-google-genai for Gemini integration.
3. Use Gemini 1.5 Flash model.
4. Each agent must be an independent node in the graph.
5. Use structured outputs (Pydantic models).
6. Implement the following agents:

   - Orchestrator Agent
   - Malware Analysis Agent
   - Network Analysis Agent
   - VirusTotal Agent (mock for now)
   - Triage Agent
   - Report Agent

7. Graph Flow:

   Input Log →
   Orchestrator →
   (Conditional edges)
       Malware Agent (if command suspicious)
       Network Agent (if IP present)
       VT Agent (if hash present)
   →
   Triage Agent →
   Report Agent →
   Final Output

8. Create a SentinelState class using TypedDict or Pydantic that stores:
   - log_data
   - agent_outputs
   - severity
   - confidence
   - final_report

9. Each agent should:
   - Accept state
   - Update state
   - Return updated state

10. Orchestrator Agent:
   - Use Gemini to classify event type
   - Return routing decision
   - Must output structured JSON:
       {
           "invoke_malware": bool,
           "invoke_network": bool,
           "invoke_vt": bool
       }

11. Malware Agent:
   - Use Gemini reasoning over command_line
   - Output:
       {
           "malware_detected": bool,
           "patterns": list,
           "mitre": list
       }

12. Network Agent:
   - Analyze destination_ip
   - Output:
       {
           "network_suspicious": bool,
           "reason": str
       }

13. VirusTotal Agent:
   - Mock logic:
       if hash == "abcd1234" → malicious
   - Return:
       {
           "vt_score": str,
           "verdict": str
       }

14. Triage Agent:
   - Combine agent outputs
   - Compute severity and confidence (LLM-assisted)
   - Output:
       {
           "severity": str,
           "confidence": float,
           "reason": str
       }

15. Report Agent:
   - Generate structured SOC-style incident report:
       {
           "incident_id": str,
           "summary": str,
           "severity": str,
           "confidence": float,
           "mitre_techniques": list,
           "timeline": list
       }

16. Create a compile_graph() function that builds and compiles the LangGraph workflow.

17. Update main.py:
   - POST /ingest
   - Invoke compiled graph
   - Return final_report

18. Use async where possible.
19. Keep code modular and clean.
20. Include example test log.

This must be production-structured and suitable for a final year project demo.


gemini api key = AIzaSyDbpA89fS7ayzCS5OLGvN6GHU5bEcO-aUs

virus total api key = 6c10d6e9d59b5b2f038704b2ef1cab447b786df1cc55e29e09b2fc020362d0c4