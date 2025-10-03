from typing import Dict, Any, List
from collections import defaultdict

from ..store import datastore


class ManufacturingInsightsAgent:
    def __init__(self, ueba):
        self.ueba = ueba

    def generate(self, latest_status: Dict[str, Any]) -> Dict[str, Any]:
        if not self.ueba.check("ManufacturingInsightsAgent", "generate_insights"):
            return {"ok": False, "error": "UEBA blocked insights"}

        # Aggregate predicted failures by component and humidity (proxy for climate)
        counts = defaultdict(int)
        humid_risk = defaultdict(list)

        for vid, status in latest_status.items():
            diag = status.get("diagnosis", {})
            comp = diag.get("top_component", "unknown")
            risk = diag.get("risk", 0.0)
            counts[comp] += 1
            telemetry = status.get("analysis", {})
            humidity = telemetry.get("anomaly_score", 0.0)
            humid_risk[comp].append(humidity)

        insights: List[Dict[str, Any]] = []
        for comp, cnt in counts.items():
            avg_humid = sum(humid_risk[comp]) / max(1, len(humid_risk[comp]))
            insights.append(
                {
                    "component": comp,
                    "predicted_issue_count": cnt,
                    "avg_anomaly_score": round(avg_humid, 2),
                    "recommendation": self._recommendation(comp, avg_humid),
                }
            )

        # Incorporate historical CAPA/RCA notes (simplified join)
        capa_rca = datastore.get_capa_rca()
        matched = []
        for rec in insights:
            comp = rec["component"]
            related = [r for r in capa_rca if r["component"] == comp]
            rec["related_capa_rca"] = related
            matched.append(rec)

        return {"ok": True, "insights": matched}

    def _recommendation(self, component: str, score: float) -> str:
        if component == "brake_system" and score > 0.6:
            return "Review pad compound and QC humid soak tests; issue service advisory for monsoon."
        if component == "battery_pack" and score > 0.5:
            return "Check cell batch QC; firmware update for charge balancing; tighten supplier CAPA."
        if component == "cooling_system" and score > 0.5:
            return "Increase inspection interval; evaluate thermostat design change."
        return "Monitor; no immediate manufacturing action."