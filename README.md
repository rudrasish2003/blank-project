# Agentic AI MVP — Autonomous Predictive Maintenance and Proactive Scheduling

This MVP implements a web-based Agentic AI with a Master Agent orchestrating Worker Agents for:
- Continuous monitoring and predictive failure detection
- Demand forecasting (simplified via usage heuristics) and autonomous scheduling
- Persuasive customer engagement (voice script simulation + browser TTS)
- RCA/CAPA insights generation and manufacturing feedback loop
- UEBA security to detect anomalous agent actions with actor context

## Quick Start

1) Install dependencies:
```
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2) Run the API server:
```
python scripts/run_server.py
```

3) Open the dashboard:
- http://localhost:8000/static/

4) (Optional) Simulate telemetry streaming via script:
```
python scripts/simulate_telematics.py
```

## Key Endpoints

- GET /             — Service info
- GET /vehicles     — List 10 synthetic vehicles
- GET /status       — Latest per-vehicle analysis/diagnosis
- POST /telemetry/{id} — Ingest telemetry; Master Agent orchestrates analysis, diagnosis, customer pitch, and slot suggestions
- GET /schedule/slots?center_id=BLR_IND — Mock available slots
- POST /schedule/book — Book a slot
  ```
  {
    "vehicle_id": "VHC-07",
    "center_id": "BLR_IND",
    "slot": "2025-10-05T10:30:00"
  }
  ```
- GET /bookings — Show booked appointments
- POST /feedback — Record CSAT and notes post-service
- GET /forecast/centers — Demand forecast per center (near/medium/low term)
- GET /insights/manufacturing — RCA/CAPA-driven insights from latest predictions
- GET /ueba/logs — UEBA audit log of agent actions and anomalies (with subject)

## Architecture Overview

- app/orchestration/master.py — MasterAgent + UEBA policy + actor context
- app/agents/* — Worker agents:
  - DataAnalysisAgent — feature engineering + anomaly score
  - DiagnosisAgent — component risk + priority/ETA
  - SchedulingAgent — proposes slots and books appointments
  - CustomerEngagementAgent — voice script + notification text
  - FeedbackAgent — records CSAT and notes
  - ManufacturingInsightsAgent — correlates predictions with CAPA/RCA
  - DemandForecastingAgent — lightweight per-center demand heuristic
- app/store/datastore.py — In-memory store backed by data/*.json
- data/*.json — Synthetic vehicles, maintenance history, and sample CAPA/RCA
- public/ — Static dashboard (index.html, styles.css, app.js) with:
  - Fleet risk view
  - Voice script playback (Web Speech API)
  - Center demand forecasts
  - Bookings list
  - Manufacturing insights
  - UEBA logs (shows subject/actor)
- scripts/run_server.py — Start FastAPI with uvicorn
- scripts/simulate_telematics.py — Send synthetic telemetry to the API

## UEBA Policy Examples

- SchedulingAgent is allowed to book slots, not read telematics.
- DataAnalysisAgent is allowed to read telematics, not book slots.
- CustomerEngagementAgent can initiate conversations, not modify scheduler capacity.

If an agent attempts an unauthorized action, UEBA logs:
```
{
  "ts": "2025-10-03T12:15:22.123Z",
  "agent": "SchedulingAgent",
  "action": "read_telematics",
  "ok": false,
  "reason": "anomalous action",
  "subject": "dashboard"
}
```

## Notes

- The MVP uses light-weight heuristics for anomaly scoring and diagnosis to keep it fast and dependency-light.
- Extend DataAnalysisAgent/DiagnosisAgent with ML as needed (e.g., Gradient Boosting + survival analysis).
- The dashboard uses browser SpeechSynthesis for voice script playback; on some systems, voice may vary.