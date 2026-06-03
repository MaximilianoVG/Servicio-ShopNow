from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.security import crear_token

router = APIRouter(tags=["Auth"])

class Login(BaseModel):
    username: str
    password: str

# Endpoint de login para obtener un token JWT
@router.post("/login")
def login(user: Login):

    if user.username != "admin" or user.password != "1234":
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = crear_token({"sub": user.username})

    return {
        "access_token": token,
        "token_type": "bearer"
    }