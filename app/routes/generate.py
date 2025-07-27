from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from openai import OpenAI
from dotenv import load_dotenv
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ..models import Post
from sqlmodel import Session, select
from ..database import engine
from .formatter import compose_post
from typing import Optional, List
from datetime import datetime, timezone
from ..worker import generate_post, generate_post_pro
from ..models import Job, User
import uuid
import json
from app.auth import get_current_user
from app.models import User
from fastapi import Depends
from app.celery_app import celery_app

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_AI_KEY"))

generate_router = APIRouter()

PLATFORM_GUIDES = {
    "twitter": "You are a social media content generator, generating a twitter post. The post should be max 280 characters, and be of typical twitter syntax.",
    "instagram": "You are a social media content generator, generating an instagra post. The post is max 2200 characters, and be of typical instagram syntax.",
    "linkedin": "You are a social media content generator, generating a linkedin post. The post is max 3000 characters, and be of typical linkedin syntax.",
    "engagement tips": "You are an expert in social media engagement, returning 4 tips for optimizing viewer engagement on a given post. The tips are max 300 characters, and focus on practical tips for optimizing engagement such as likes, comments, and shares.",
}

class PromptInput(BaseModel):
    prompt: str
    tone: Optional[str] = "default"
    length: Optional[str] = "default"

user_generation_count = {}
FREE_LIMIT = 5
PRO_LIMIT = 30

def generate_response_pro(input: PromptInput, user_id = None):
    platforms = ['twitter', 'linkedin', 'instagram', 'engagement tips']
    outputs = {}
    total_tokens = 0

    for platform in platforms:
        result = compose_post(input.prompt, platform, input.tone, input.length)
        outputs[platform] = result["content"]
        total_tokens += result["tokens_used"]

    outputs["tokens_used"] = total_tokens

    post = Post(
        prompt=input.prompt,
        tone=input.tone,
        length=input.length,
        tokens_used=total_tokens,
        user_id=user_id,
        platform_outputs=outputs,
        created_at=datetime.now(timezone.utc)
    )

    with Session(engine) as session:
        session.add(post)
        session.commit()
        session.refresh(post)

    return outputs

def generate_response(input: PromptInput, user_id = None):
    platforms = ['twitter', 'linkedin', 'instagram']
    outputs = {}
    total_tokens = 0

    for platform in platforms:
        result = compose_post(input.prompt, platform, input.tone, input.length)
        outputs[platform] = result["content"]
        total_tokens += result["tokens_used"]

    outputs["tokens_used"] = total_tokens

    post = Post(
        prompt=input.prompt,
        tone=input.tone,
        length=input.length,
        tokens_used=total_tokens,
        user_id=user_id,
        platform_outputs=outputs,
        created_at=datetime.now(timezone.utc)
    )

    with Session(engine) as session:
        session.add(post)
        session.commit()
        session.refresh(post)

    return outputs

@generate_router.post("/generate")
def generate_nolimit(input: PromptInput):
    task = generate_post.delay(input.prompt, input.tone, input.length)
    with Session(engine) as session:
        job = Job(id=task.id, status="PENDING")
        session.add(job)
        session.commit()

        return {"job_id": task.id}  

@generate_router.post("/result/{job_id}")
def get_result(job_id: str):
    with Session(engine) as session:
        job = session.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        result = job.result
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                pass
        return {
            "status": job.status,
            "result": result,
            "job_id": job.id
        }


@generate_router.post("/generate/{user_id}")
def generate_with_limit(input: PromptInput, user: User = Depends(get_current_user)):
    with Session(engine) as session:
        user = session.get(User, user.id)
        if not user:
            user = User(
                id=user.id, 
                name = f"Free User {user.id}",
                email = f"freeuser{user.id}@example.com",
                password = f"password{user.id}",
                tier="free"
            )
            session.add(user)
            session.commit()
        
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        result = session.exec(
            select(Post).where(
                Post.user_id == user.id,
                Post.created_at >= start_of_month
            )
        )
        count = len(result.all())

        tier_limits = {
            "free": 5,
            "pro": 30,
            "unlimited": 300
        }

        if count >= tier_limits[user.tier]:
            raise HTTPException(status_code=403, 
            detail = f'{user.tier.capitalize()} limit reached, upgrade to a paid plan to generate more posts')
        
        if user.tier == "pro" or user.tier == "unlimited":
            task = generate_post_pro.delay(input.prompt, input.tone, input.length, user.id)
        else:
            task = generate_post.delay(input.prompt, input.tone, input.length, user.id)

        with Session(engine) as session:
            job = Job(id=task.id, status="PENDING")
            session.add(job)
            session.commit()

        return {"job_id": task.id}

            

      


@generate_router.get("/posts", response_model=List[Post])
def get_posts():
    with Session(engine) as session:
        posts = session.exec(select(Post).order_by(Post.created_at.desc())).all()
        return posts 