from typing import Dict, Any, List
from collections import defaultdict
from datetime import datetime

from ..store import datastore


class DemandForecastingAgent:
    def __init__(self, ueba):
        self.ueba = ueba

    def forecast(self) -> Dict[str, Any]:
        # UEBA: treat this as read_history
        if not self.ueba.check("DataAnalysisAgent", "read_history"):
            return {"ok": False, "error": "UEBA blocked history read"}

        vehicles = datastore.list_vehicles()
        status = datastore.get_all_status()

        # Simple heuristics:
        # - Priority High/Medium vehicles -> near-term demand
        # - City -> center mapping
        center_map = {"BLR": "BLR_IND", "MUM": "MUM_AND", "DEL": "DEL_SAK"}
        centers = defaultdict(lambda: {"near_term": 0, "medium_term": 0, "low_term": 0})

        for v in vehicles:
            vid = v["id"]
            s = status.get(vid, {})
            diag = s.get("diagnosis", {})
            priority = diag.get("priority", "Low")
            center_id = center_map.get(v.get("city", "BLR"), "BLR_IND")
            if priority == "High":
                centers[center_id]["near_term"] += 1
            elif priority == "Medium":
                centers[center_id]["medium_term"] += 1
            else:
                centers[center_id]["low_term"] += 1

        # Convert to list
        out: List[Dict[str, Any]] = []
        for cid, agg in centers.items():
            out.append(
                {
                    "center_id": cid,
                    "near_term": agg["near_term"],
                    "medium_term": agg["medium_term"],
                    "low_term": agg["low_term"],
                    "generated_at": datetime.utcnow().isoformat(),
                }
            )

        return {"ok": True, "centers": out}