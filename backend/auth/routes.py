from fastapi import APIRouter, Depends, HTTPException
from auth.models import RegisterUser, LoginUser
from auth.utils import hash_password, verify_password, create_jwt
from database.mongo import get_db
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError
from fastapi import APIRouter, WebSocket


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
async def register(user: RegisterUser, db=Depends(get_db)):
    if db.clients.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_data = user.dict()
    user_data["hashed_password"] = hash_password(user_data.pop("password"))
    result = db.clients.insert_one(user_data)

    token = create_jwt({"client_id": str(result.inserted_id), "email": user.email})
    return {"token": token}

@router.post("/login")
async def login(user: LoginUser, db=Depends(get_db)):
    existing = db.clients.find_one({"email": user.email})
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user.password, existing["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt({"client_id": str(existing["_id"]), "email": user.email})
    return {"token": token}




