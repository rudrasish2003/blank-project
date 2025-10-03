from typing import Dict, Any


class CustomerEngagementAgent:
    def __init__(self, ueba):
        self.ueba = ueba

    def compose_pitch(self, vehicle_id: str, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        if not self.ueba.check("CustomerEngagementAgent", "initiate_conversation"):
            return {"ok": False, "error": "UEBA blocked conversation"}

        comp = diagnosis.get("top_component", "brake_system")
        risk = diagnosis.get("risk", 0.0)
        priority = diagnosis.get("priority", "Low")
        eta = diagnosis.get("eta_days", 14)

        script = [
            f"Hi there! We've detected elevated risk ({risk:.2f}) in your {comp.replace('_', ' ')}.",
            f"To avoid downtime and cost, we recommend a quick service within {eta} days (priority: {priority}).",
            "Would you like me to schedule an appointment at the nearest service center?",
        ]
        notification = "App notification queued: predictive check recommended; tap to book now."

        return {"ok": True, "voice_script": script, "notification": notification}