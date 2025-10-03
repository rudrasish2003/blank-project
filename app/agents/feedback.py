from typing import Dict, Any
from datetime import datetime

from ..store import datastore


class FeedbackAgent:
    def __init__(self, ueba):
        self.ueba = ueba

    def record(self, vehicle_id: str, csat: int, notes: str) -> Dict[str, Any]:
        if not self.ueba.check("FeedbackAgent", "record_feedback"):
            return {"ok": False, "error": "UEBA blocked feedback"}

        entry = {
            "vehicle_id": vehicle_id,
            "csat": csat,
            "notes": notes,
            "ts": datetime.utcnow().isoformat(),
        }
        datastore.add_feedback(entry)
        return {"ok": True, "feedback": entry}