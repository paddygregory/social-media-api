from celery import Celery
from sqlmodel import Session
from app.database import engine
from app.models import Post, Job
from app.routes.formatter import compose_post
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
import multiprocessing as mp

try:
    mp.set_start_method("forkserver", force=True)
except RuntimeError:
    pass  # already set on import
  
load_dotenv()

celery_app = Celery(
    "worker",
    broker=os.getenv("REDIS_BROKER_URL"),
    backend=os.getenv("REDIS_BACKEND_URL")
)

@celery_app.task(bind=True)
def generate_post(self, prompt: str, tone: str, length: str, user_id: int):
    from app.models import Job
    job_id = self.request.id

    try:
        platforms = ['twitter', 'linkedin', 'instagram']
        outputs = {}
        total_tokens = 0

        for platform in platforms:
            result = compose_post(prompt, platform, tone, length)
            outputs[platform] = result["content"]
            total_tokens += result["tokens_used"]

        
        with Session(engine) as session:
            post = Post(
                prompt=prompt,
                tone=tone,
                length=length,
                tokens_used=total_tokens,
                user_id=user_id,
                platform_outputs=outputs,
                created_at=datetime.now(timezone.utc)
            )
            session.add(post)

            job = session.get(Job, job_id)
            if job:
                job.status = "SUCCESS"
                job.result = outputs
                session.add(job)

            session.commit()

        return outputs

    except Exception as e:
        with Session(engine) as session:
            job = session.get(Job, job_id)
            if job:
                job.status = "FAILED"
                job.result = str(e)
                session.add(job)
                session.commit()
        raise e

@celery_app.task(bind=True)
def generate_post_pro(self, prompt: str, tone: str, length: str, user_id: int):
    from app.models import Job
    job_id = self.request.id

    try:
        platforms = ['twitter', 'linkedin', 'instagram', 'engagement tips']
        outputs = {}
        total_tokens = 0

        for platform in platforms:
            result = compose_post(prompt, platform, tone, length)
            outputs[platform] = result["content"]
            total_tokens += result["tokens_used"]

        
        with Session(engine) as session:
            post = Post(
                prompt=prompt,
                tone=tone,
                length=length,
                tokens_used=total_tokens,
                user_id=user_id,
                platform_outputs=outputs,
                created_at=datetime.now(timezone.utc)
            )
            session.add(post)

            job = session.get(Job, job_id)
            if job:
                job.status = "SUCCESS"
                job.result = outputs
                session.add(job)

            session.commit()

        return outputs

    except Exception as e:
        with Session(engine) as session:
            job = session.get(Job, job_id)
            if job:
                job.status = "FAILED"
                job.result = str(e)
                session.add(job)
                session.commit()
        raise e
    
