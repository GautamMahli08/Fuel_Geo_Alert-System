from pydantic import BaseModel
from typing import List
from bson import ObjectId

class Point(BaseModel):
    lat: float
    lng: float

class VehicleCreate(BaseModel):
    vehicle_number: str
    sensor_id: str
    fuel_tank_capacity: float
    assigned_driver: str
    geofence: List[Point]  # List of lat/lng

class VehicleInDB(VehicleCreate):
    client_id: str  # from JWT
