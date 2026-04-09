from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.client import client_router
from app.routers.admin import admin_router
from app.routers.webapp.auth import router as webapp_router
from app.routers.webapp.miniapp import router as miniapp_router

app = FastAPI(title="Salon API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://your-real-domain.com",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(client_router)
app.include_router(admin_router)
app.include_router(webapp_router)
app.include_router(miniapp_router)
