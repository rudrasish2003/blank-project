from typing import Dict, Any, List
import json
import os


class DataStore:
    def __init__(self):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base, "..", "data")
        self.vehicles_path = os.path.join(data_dir, "vehicles.json")
        self.maintenance_path = os.path.join(data_dir, "maintenance.json")
        self.capa_rca_path = os.path.join(data_dir, "capa_rca.json")

        self._vehicles: Dict[str, Any] = self._read_json(self.vehicles_path)
        self._maintenance: List[Dict[str, Any]] = self._read_json(self.maintenance_path)
        self._capa_rca: List[Dict[str, Any]] = self._read_json(self.capa_rca_path)

        self._status: Dict[str, Any] = {}  # latest analysis/diagnosis per vehicle
        self._bookings: List[Dict[str, Any]] = []
        self._feedback: List[Dict[str, Any]] = []

    def _read_json(self, path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return {} if path.endswith("vehicles.json") else []

    # Vehicles
    def list_vehicles(self) -> List[Dict[str, Any]]:
        return list(self._vehicles.values())

    def get_vehicle(self, vehicle_id: str) -> Dict[str, Any]:
        return self._vehicles.get(vehicle_id)

    # Status
    def update_status(self, vehicle_id: str, status: Dict[str, Any]):
        self._status[vehicle_id] = {**self._status.get(vehicle_id, {}), **status}

    def get_status(self, vehicle_id: str) -> Dict[str, Any]:
        return self._status.get(vehicle_id, {})

    def get_all_status(self) -> Dict[str, Any]:
        return self._status

    # Bookings
    def add_booking(self, booking: Dict[str, Any]):
        self._bookings.append(booking)

    # Feedback
    def add_feedback(self, entry: Dict[str, Any]):
        self._feedback.append(entry)

    # CAPA/RCA
    def get_capa_rca(self) -> List[Dict[str, Any]]:
        return self._capa_rca


datastore = DataStore()