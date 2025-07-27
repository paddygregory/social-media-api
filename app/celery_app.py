
import os
from celery import Celery

broker_url   = os.getenv("REDIS_BROKER_URL")
backend_url  = os.getenv("REDIS_BACKEND_URL", broker_url)   

celery_app = Celery("worker", broker=broker_url, backend=backend_url)


if broker_url.startswith("rediss://"):
    celery_app.conf.broker_use_ssl = {"ssl_cert_reqs": None}  


if backend_url.startswith("rediss://"):
    celery_app.conf.redis_backend_use_ssl = {"ssl_cert_reqs": None}