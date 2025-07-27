from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from auth.routes import router as auth_router
from vehicles.routes import router as vehicle_router
from mqtt.routes import router as mqtt_router
from websocket.ws_routes import router as ws_router

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(vehicle_router)
app.include_router(auth_router)
app.include_router(vehicle_router)
app.include_router(mqtt_router)

app.include_router(auth_router)
app.include_router(vehicle_router)
app.include_router(mqtt_router)
app.include_router(ws_router)
@app.get("/")
async def root():
    return {"message": "Vehicle Monitoring API"}
