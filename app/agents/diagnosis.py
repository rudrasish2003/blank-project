from typing import Dict, Any


class DiagnosisAgent:
    def __init__(self, ueba):
        self.ueba = ueba

    def assess(self, vehicle_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        if not self.ueba.check("DiagnosisAgent", "run_models"):
            return {"ok": False, "error": "UEBA blocked diagnosis"}

        score = analysis.get("anomaly_score", 0.0)
        # Map score to component risks
        risks = {
            "brake_system": min(1.0, max(0.0, score * 1.2)),
            "battery_pack": min(1.0, max(0.0, (score - 0.2) * 1.1)),
            "cooling_system": min(1.0, max(0.0, (score - 0.1) * 1.0)),
        }

        # Priority based on maximum risk + simple rule
        max_comp = max(risks, key=risks.get)
        max_risk = risks[max_comp]
        if max_risk > 0.75:
            priority = "High"
            eta_days = 7
        elif max_risk > 0.45:
            priority = "Medium"
            eta_days = 14
        else:
            priority = "Low"
            eta_days = 30

        diagnosis = {
            "component_risks": {k: round(v, 2) for k, v in risks.items()},
            "top_component": max_comp,
            "risk": round(max_risk, 2),
            "priority": priority,
            "eta_days": eta_days,
        }
        return diagnosis