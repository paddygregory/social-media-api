from fastapi import APIRouter, Request
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.responses import RedirectResponse
from app.database import get_or_create_user
from app.auth import create_access_token

import os
from dotenv import load_dotenv

load_dotenv()


google_router = APIRouter()
config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name = 'google',
    client_id = os.getenv('GOOGLE_CLIENT_ID'),
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url = 'https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs = {
        'scope': 'openid email profile' ,
    }
)

@google_router.get('/auth/google')
async def login(request: Request):
    redirect_uri = request.url_for('auth_google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@google_router.get('/auth/google/callback')
async def auth_google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.parse_id_token(request, token)

    user = await get_or_create_user(user_info)
    jwt = create_access_token({'sub': str(user.id)})

    response = RedirectResponse(url=f"https://socialai.paddymgregory.com/login-success#token={jwt}")
    return response

