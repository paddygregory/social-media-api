from fastapi import APIRouter, Request, Depends
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.responses import RedirectResponse
from app.database import get_or_create_user
from app.auth import create_access_token

google_router = APIRouter()

config = Config(".env")
oauth = OAuth(config)

GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET")