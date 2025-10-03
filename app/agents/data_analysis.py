from typing import Dict, Any
from datetime import datetime


class DataAnalysisAgent:
    def __init__(self, ueba):
        self.ueba = ueba

    def analyze(self, vehicle_id: str, telemetry: Dict[str, float]) -> Dict[str, Any]:
        if not self.ueba.check("DataAnalysisAgent", "read_telematics"):
            return {"ok": False, "error": "UEBA blocked telematics read"}

        # Simple feature engineering and anomaly scoring
        # Normalize inputs and compute weighted anomaly score
        weights = {
            "rpm": 0.1,
            "brake_pad_wear": 0.3,
            "battery_voltage": 0.15,
            "coolant_temp": 0.2,
            "vibration": 0.15,
            "ambient_humidity": 0.05,
            "duty_cycle_factor": 0.05,
        }

        # Anomaly heuristics — distance from typical healthy ranges
        def metric(name, value):
            if name == "rpm":
                base = abs(value - 2200) / 2200
            elif name == "brake_pad_wear":
                base = value  # 0-1 wear proportion
            elif name == "battery_voltage":
                base = abs(value - 12.5) / 12.5
            elif name == "coolant_temp":
                base = max(0.0, (value - 95) / 95)
            elif name == "vibration":
                base = value / 10.0
            elif name == "ambient_humidity":
                base = value / 100.0
            elif name == "duty_cycle_factor":
                base = value
            else:
                base = 0.0
            return weights.get(name, 0.0) * base

        score = sum(metric(k, telemetry.get(k, 0.0)) for k in weights.keys())
        score = max(0.0, min(1.0, score))

        features = {
            "anomaly_score": round(score, 3),
            "mileage_km": telemetry.get("mileage_km", 0.0),
            "ts": datetime.utcnow().isoformat(),
        }

        return features