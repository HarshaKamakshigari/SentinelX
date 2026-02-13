We are building a live SOC dashboard for the SentinelX Agentic SOC system using Next.js (App Router).

Tech Stack:
- Next.js 14 (App Router)
- Axios for API calls
- Functional components + React Hooks
- Tailwind CSS for styling
- No heavy UI libraries

Backend:
GET http://localhost:8000/incidents
Returns:
[
  {
    "incident_id": "SOC-2026-001",
    "severity": "HIGH",
    "confidence": 0.92,
    "summary": "Encoded PowerShell with outbound traffic",
    "mitre_techniques": ["T1059.001", "T1071"],
    "agents_invoked": ["MalwareAgent", "NetworkAgent", "VTAgent"],
    "timestamp": "2026-02-13T10:22:00"
  }
]

Requirements:

1. Create a modern dark SOC-style dashboard.
2. Poll backend every 3 seconds using useEffect + setInterval.
3. Use client components where necessary ("use client").
4. Display at top:
   - Total Incidents
   - High count
   - Medium count
   - Low count

5. Display main incident table with:
   - Incident ID
   - Severity (color-coded:
       HIGH → red
       MEDIUM → orange
       LOW → green)
   - Confidence
   - Timestamp

6. Clicking a row should open a right-side sliding detail panel showing:
   - Summary
   - Confidence
   - MITRE techniques
   - Agents involved
   - Timestamp

7. Create the following structure:

   src/app/page.js
   src/components/StatsCards.jsx
   src/components/IncidentTable.jsx
   src/components/IncidentDetails.jsx

8. Use Tailwind styling:
   - Background: bg-slate-900
   - Cards: bg-slate-800 with rounded-xl and shadow
   - Smooth hover effects
   - Smooth transition for detail panel

9. Use React state to:
   - Store incidents
   - Store selected incident
   - Compute severity counts dynamically

10. Handle empty state:
   If no incidents, show:
   "No incidents detected"

11. Ensure code is clean, production-ready, and suitable for final year project demo.

12. Add loading state while fetching incidents.

Generate complete working code.
