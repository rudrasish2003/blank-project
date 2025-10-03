from typing import List, Dict, Any
from datetime import datetime, timedelta

from ..store import datastore


class SchedulingAgent:
    def __init__(self, ueba):
        self.ueba = ueba
        # Mock capacity per center
        self.centers = {
            "BLR_IND": "Bengaluru Indiranagar",
            "BLR_ELC": "Bengaluru Electronic City",
            "MUM_AND": "Mumbai Andheri",
            "DEL_SAK": "Delhi Saket",
        }

    def get_slots(self, center_id: str) -> List[str]:
        if not self.ueba.check("SchedulingAgent", "read_capacity"):
            return []

        # Next 5 slots every 2 hours starting tomorrow 9AM
        base = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return [(base + timedelta(hours=i * 2)).isoformat() for i in range(5)]

    def propose_slots(self, vehicle_id: str, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        # Balance urgency and distance (mock: pick center by city)
        v = datastore.get_vehicle(vehicle_id)
        city = v.get("city", "BLR")
        center_map = {"BLR": "BLR_IND", "MUM": "MUM_AND", "DEL": "DEL_SAK"}
        center_id = center_map.get(city, "BLR_IND")

        slots = self.get_slots(center_id)
        return {"center_id": center_id, "center_name": self.centers[center_id], "slots": slots}

    def book(self, vehicle_id: str, center_id: str, slot: str) -> Dict[str, Any]:
        if not self.ueba.check("SchedulingAgent", "book_slot"):
            return {"ok": False, "error": "UEBA blocked booking"}

        # Simple validation
        if center_id not in self.centers:
            return {"ok": False, "error": "Unknown center"}

        # Record booking
        booking = {
            "vehicle_id": vehicle_id,
            "center_id": center_id,
            "center_name": self.centers[center_id],
            "slot": slot,
            "created_at": datetime.utcnow().isoformat(),
        }
        datastore.add_booking(booking)
        return {"ok": True, "booking": booking}