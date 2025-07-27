from fastapi import APIRouter, Depends, HTTPException
from vehicles.models import VehicleCreate
from database.mongo import get_db
from auth.utils import jwt
from fastapi.security import OAuth2PasswordBearer
import os

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
SECRET_KEY = os.getenv("SECRET_KEY")

def get_current_client(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["client_id"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/register")
async def register_vehicle(vehicle: VehicleCreate, db=Depends(get_db), client_id=Depends(get_current_client)):
    vehicle_dict = vehicle.dict()
    vehicle_dict["client_id"] = client_id

    if db.vehicles.find_one({"sensor_id": vehicle.sensor_id}):
        raise HTTPException(status_code=400, detail="Sensor ID already in use")

    result = db.vehicles.insert_one(vehicle_dict)
    return {"message": "Vehicle registered", "vehicle_id": str(result.inserted_id)}

def get_current_client(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return payload["client_id"]

@router.get("/my")
async def get_my_vehicles(db=Depends(get_db), client_id=Depends(get_current_client)):
    vehicles = list(db.vehicles.find({"client_id": client_id}))
    for v in vehicles:
        v["_id"] = str(v["_id"])
    return vehicles
