from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os

from app.routes.health import health_router
from app.routes.template import template_router
from app.routes.generate import generate_router
from app.routes.payments import payments_router
from app.routes.auth2 import auth_router
from app.routes.google_auth import google_router
from app.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

# Add session middleware for OAuth
app.add_middleware(
    SessionMiddleware, 
    secret_key=os.getenv("JWT_SECRET_KEY", "supersecret")
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://socialai.paddymgregory.com",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Routers
app.include_router(health_router)
app.include_router(template_router)
app.include_router(generate_router)
app.include_router(payments_router)
app.include_router(auth_router)
app.include_router(google_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


