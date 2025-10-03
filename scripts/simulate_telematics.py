import time
import random
import requests

BASE = "http://localhost:8000"


def gen_payload(risk_bias=0.3):
    # Generate synthetic telemetry with tunable risk bias
    return {
        "rpm": random.uniform(1800, 3200),
        "brake_pad_wear": min(1.0, random.random() * (0.4 + risk_bias)),
        "battery_voltage": random.uniform(11.8 - risk_bias, 12.8 + risk_bias),
        "coolant_temp": random.uniform(85, 110 + risk_bias * 20),
        "vibration": random.uniform(1.0, 8.0 + risk_bias * 5),
        "ambient_humidity": random.uniform(30, 90),
        "mileage_km": random.uniform(10000, 65000),
        "duty_cycle_factor": random.uniform(0.2, 0.9),
    }


def send(vehicle_id: str, payload: dict):
    r = requests.post(f"{BASE}/telemetry/{vehicle_id}", json=payload, timeout=5)
    print(vehicle_id, r.status_code, r.json())


if __name__ == "__main__":
    vehicles = ["VHC-01", "VHC-03", "VHC-07", "VHC-10"]
    for _ in range(3):
        for vid in vehicles:
            send(vid, gen_payload(risk_bias=0.4 if vid in ("VHC-07", "VHC-10") else 0.2))
        time.sleep(1.5)