from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Dict, Any, List
from pydantic import BaseModel

from .orchestration.master import MasterAgent, UEBAEvent
from .store import datastore

app = FastAPI(title="Agentic AI MVP — Predictive Maintenance & Scheduling")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static dashboard assets from /static
app.mount("/static", StaticFiles(directory="public"), name="static")


class TelemetryPayload(BaseModel):
    rpm: float
    brake_pad_wear: float  # 0-1
    battery_voltage: float
    coolant_temp: float
    vibration: float
    ambient_humidity: float
    mileage_km: float
    duty_cycle_factor: float  # 0-1 relative usage intensity


class BookingRequest(BaseModel):
    vehicle_id: str
    center_id: str
    slot: str  # ISO timestamp string


class FeedbackPayload(BaseModel):
    vehicle_id: str
    csat: int
    notes: str


master = MasterAgent()


@app.get("/vehicles")
def list_vehicles() -> List[Dict[str, Any]]:
    return datastore.list_vehicles()


@app.get("/status")
def all_status() -> Dict[str, Any]:
    return master.mfg_insights.ueba.get_logs() and datastore.get_all_status()  # force UEBA type usage


@app.get("/vehicles/{vehicle_id}")
def vehicle_status(vehicle_id: str) -> Dict[str, Any]:
    v = datastore.get_vehicle(vehicle_id)
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    status = master.get_vehicle_status(vehicle_id)
    return {"vehicle": v, "status": status}


@app.post("/telemetry/{vehicle_id}")
def ingest_telemetry(vehicle_id: str, payload: TelemetryPayload) -> Dict[str, Any]:
    if not datastore.get_vehicle(vehicle_id):
        raise HTTPException(status_code=404, detail="Vehicle not found")

    result = master.process_telematics(vehicle_id, payload.model_dump())
    return result


@app.get("/schedule/slots")
def get_slots(center_id: str) -> Dict[str, Any]:
    slots = master.get_available_slots(center_id)
    return {"center_id": center_id, "slots": slots}


@app.post("/schedule/book")
def book_slot(req: BookingRequest) -> Dict[str, Any]:
    booking = master.book_slot(req.vehicle_id, req.center_id, req.slot)
    if not booking["ok"]:
        raise HTTPException(status_code=400, detail=booking["error"])
    return booking


@app.get("/bookings")
def list_bookings() -> List[Dict[str, Any]]:
    # Expose bookings from datastore
    # Note: minimal exposure for dashboard visualization
    from .store import datastore as ds

    return getattr(ds, "_bookings", [])


@app.post("/feedback")
def submit_feedback(payload: FeedbackPayload) -> Dict[str, Any]:
    resp = master.capture_feedback(payload.vehicle_id, payload.csat, payload.notes)
    return resp


@app.get("/insights/manufacturing")
def manufacturing_insights() -> Dict[str, Any]:
    return master.generate_manufacturing_insights()


@app.get("/ueba/logs")
def ueba_logs() -> List[UEBAEvent]:
    return master.ueba.get_logs()


@app.get("/")
def root():
    return {
        "message": "Agentic AI MVP running",
        "dashboard": "/static/",
        "endpoints": [
            "GET /vehicles",
            "GET /vehicles/{vehicle_id}",
            "GET /status",
            "POST /telemetry/{vehicle_id}",
            "GET /schedule/slots?center_id=",
            "POST /schedule/book",
            "GET /bookings",
            "POST /feedback",
            "GET /insights/manufacturing",
            "GET /ueba/logs",
        ],
    }