from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from auth.utils import jwt
from websocket.manager import manager
import os

router = APIRouter()
SECRET_KEY = os.getenv("SECRET_KEY")

def get_client_id_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["client_id"]
    except Exception as e:
        print("JWT decode error:", e)
        return None

async def websocket_auth(websocket: WebSocket):
    token = websocket.query_params.get("token")
    client_id = get_client_id_from_token(token)
    if not client_id:
        await websocket.close(code=1008)
    return client_id

async def websocket_endpoint(websocket: WebSocket):
    client_id = await websocket_auth(websocket)
    if not client_id:
        return

    await manager.connect(client_id, websocket)
    print(f"🟢 WebSocket connected: client_id = {client_id}")

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        print(f"🔴 WebSocket disconnected: client_id = {client_id}")
        manager.disconnect(client_id, websocket)

# ✅ This registers the /ws/alerts endpoint
@router.websocket("/ws/alerts")
async def ws_alerts(websocket: WebSocket):
    await websocket_endpoint(websocket)
