# backend/websocket/ws_routes.py

from fastapi import APIRouter, WebSocket
from .routes import websocket_endpoint  # This is from websocket/routes.py

router = APIRouter()

@router.websocket("/ws/alerts")
async def alert_ws(websocket: WebSocket):
    await websocket_endpoint(websocket)
