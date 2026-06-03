from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth
from app.routers import (
    pedidos_v1,
    pedidos_v2
)

app = FastAPI(
    title="Pedidos Service"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(pedidos_v1.router)
app.include_router(pedidos_v2.router)

