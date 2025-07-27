from fastapi import APIRouter, Depends, HTTPException, WebSocket
from pydantic import BaseModel
from typing import Optional
from database.mongo import get_db
from datetime import datetime
from shapely.geometry import Point, Polygon
from websocket.manager import manager
import logging

router = APIRouter(prefix="/sensor", tags=["Sensor"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SensorPayload(BaseModel):
    sensor_id: str
    fuel_level: float
    valve_open: bool
    latitude: float
    longitude: float
    tilt_detected: bool
    timestamp: Optional[datetime] = None

@router.get("/latest/{sensor_id}")
async def get_latest_sensor_data(sensor_id: str, db=Depends(get_db)):
    data = db.sensor_data.find_one({"sensor_id": sensor_id}, sort=[("timestamp", -1)])
    if not data:
        raise HTTPException(status_code=404, detail="No data found")
    data["_id"] = str(data["_id"])
    return data

@router.post("/ingest")
async def ingest_sensor_data(payload: SensorPayload, db=Depends(get_db)):
    try:
        vehicle = db.vehicles.find_one({"sensor_id": payload.sensor_id})
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found for this sensor")

        if payload.timestamp is None:
            payload.timestamp = datetime.utcnow()

        db.sensor_data.insert_one(payload.dict())

        alerts = []

        # --- Fuel Theft Detection ---
        last = db.sensor_data.find({"sensor_id": payload.sensor_id}).sort("timestamp", -1).limit(2)
        last_data = list(last)
        if len(last_data) == 2:
            prev = last_data[1]
            fuel_drop = prev["fuel_level"] - payload.fuel_level
            if fuel_drop > 10 and payload.valve_open:
                alerts.append("Fuel Theft Detected")

        # --- Geofence Violation Detection ---
        try:
            geofence_coords = [(p["lng"], p["lat"]) for p in vehicle.get("geofence", []) if "lng" in p and "lat" in p]
            if not geofence_coords:
                logger.warning(f"Geofence is empty or malformed for sensor {payload.sensor_id}")
            else:
                point = Point(payload.longitude, payload.latitude)
                poly = Polygon(geofence_coords)
                if not poly.contains(point):
                    alerts.append("Geofence Breach Detected")
        except Exception as e:
            logger.error(f"Error in geofence check: {e}")

        # --- Tampering Detection ---
        hour = payload.timestamp.hour
        if payload.valve_open and (hour >= 21 or hour <= 6):
            alerts.append("Tampering Detected (Valve Open at Unauthorized Time)")

        # Store alerts in DB and push via WebSocket
        for alert in alerts:
            alert_doc = {
                "sensor_id": payload.sensor_id,
                "vehicle_id": vehicle["_id"],
                "alert": alert,
                "timestamp": payload.timestamp
            }
            db.alerts.insert_one(alert_doc)

            await manager.send_alert(
                client_id=str(vehicle["client_id"]),
                alert_data={
                    "alert": alert,
                    "sensor_id": payload.sensor_id,
                    "vehicle_id": str(vehicle["_id"]),
                    "timestamp": str(payload.timestamp),
                }
            )
            logger.info(f"🚨 WebSocket alert sent to {vehicle['client_id']}: {alert}")

        return {
            "message": "Data ingested",
            "alerts": alerts
        }

    except Exception as e:
        logger.exception("Unhandled error in /sensor/ingest")
        raise HTTPException(status_code=500, detail=str(e))
