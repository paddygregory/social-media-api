import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from .models import Post
from fastapi import FastAPI
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.routes.health import health_router
from app.routes.template import template_router
from app.routes.generate import generate_router
from app.routes.payments import payments_router
from .database import engine, create_db_and_tables 
import uvicorn

from app.routes.auth2 import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(health_router)
app.include_router(template_router)
app.include_router(generate_router)
app.include_router(payments_router)
app.include_router(auth_router)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

