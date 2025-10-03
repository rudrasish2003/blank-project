from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..agents.data_analysis import DataAnalysisAgent
from ..agents.diagnosis import DiagnosisAgent
from ..agents.scheduling import SchedulingAgent
from ..agents.customer_engagement import CustomerEngagementAgent
from ..agents.feedback import FeedbackAgent
from ..agents.manufacturing_insights import ManufacturingInsightsAgent
from ..store import datastore


@dataclass
class UEBAEvent:
    ts: str
    agent: str
    action: str
    ok: bool
    reason: str


class UEBA:
    def __init__(self):
        # Define allowed actions per agent
        self.policy = {
            "MasterAgent": {"orchestrate", "audit_log"},
            "DataAnalysisAgent": {"read_telematics", "read_history", "emit_alert"},
            "DiagnosisAgent": {"run_models"},
            "SchedulingAgent": {"read_capacity", "book_slot"},
            "CustomerEngagementAgent": {"initiate_conversation", "send_notification"},
            "FeedbackAgent": {"record_feedback"},
            "ManufacturingInsightsAgent": {"generate_insights"},
        }
        self._logs: List[UEBAEvent] = []

    def check(self, agent: str, action: str) -> bool:
        ok = action in self.policy.get(agent, set())
        self._logs.append(
            UEBAEvent(
                ts=datetime.utcnow().isoformat(),
                agent=agent,
                action=action,
                ok=ok,
                reason="allowed" if ok else "anomalous action",
            )
        )
        return ok

    def get_logs(self) -> List[UEBAEvent]:
        return self._logs


class MasterAgent:
    def __init__(self):
        self.ueba = UEBA()
        self.data_analysis = DataAnalysisAgent(self.ueba)
        self.diagnosis = DiagnosisAgent(self.ueba)
        self.scheduling = SchedulingAgent(self.ueba)
        self.customer = CustomerEngagementAgent(self.ueba)
        self.feedback = FeedbackAgent(self.ueba)
        self.mfg_insights = ManufacturingInsightsAgent(self.ueba)

    def get_vehicle_status(self, vehicle_id: str) -> Dict[str, Any]:
        return datastore.get_status(vehicle_id)

    def process_telematics(self, vehicle_id: str, telemetry: Dict[str, float]) -> Dict[str, Any]:
        if not self.ueba.check("MasterAgent", "orchestrate"):
            return {"ok": False, "error": "UEBA blocked orchestration"}

        # 1) Data analysis
        analysis = self.data_analysis.analyze(vehicle_id, telemetry)

        # 2) Diagnosis
        diagnosis = self.diagnosis.assess(vehicle_id, analysis)

        # Update status store
        datastore.update_status(vehicle_id, {"analysis": analysis, "diagnosis": diagnosis})

        # 3) Decide engagement/scheduling threshold
        if diagnosis["priority"] in ("High", "Medium"):
            convo = self.customer.compose_pitch(vehicle_id, diagnosis)
            suggestion = self.scheduling.propose_slots(vehicle_id, diagnosis)
            result = {
                "ok": True,
                "analysis": analysis,
                "diagnosis": diagnosis,
                "customer_pitch": convo,
                "scheduling": suggestion,
            }
        else:
            result = {"ok": True, "analysis": analysis, "diagnosis": diagnosis}

        return result

    def get_available_slots(self, center_id: str) -> List[str]:
        return self.scheduling.get_slots(center_id)

    def book_slot(self, vehicle_id: str, center_id: str, slot: str) -> Dict[str, Any]:
        return self.scheduling.book(vehicle_id, center_id, slot)

    def capture_feedback(self, vehicle_id: str, csat: int, notes: str) -> Dict[str, Any]:
        return self.feedback.record(vehicle_id, csat, notes)

    def generate_manufacturing_insights(self) -> Dict[str, Any]:
        # Combine latest diagnostics + historical CAPA/RCA to produce insights
        latest = datastore.get_all_status()
        return self.mfg_insights.generate(latest)