
from sqlmodel import Session
from app.database import engine
from app.models import Post, Job
from app.routes.formatter import compose_post
from datetime import datetime, timezone
from app.celery_app import celery_app  


@celery_app.task(bind=True)
def generate_post(self, prompt: str, tone: str, length: str, user_id: int):
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
