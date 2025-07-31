import os, sys
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.health import health_router
from app.routes.template import template_router
from app.routes.generate import generate_router
from app.routes.payments import payments_router
from app.routes.auth2 import auth_router
from app.database import create_db_and_tables, get_or_create_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


