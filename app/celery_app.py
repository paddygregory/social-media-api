
import os, ssl
from celery import Celery

broker_url  = os.getenv("REDIS_BROKER_URL")                      
backend_url = os.getenv("REDIS_BACKEND_URL", broker_url)        


ssl_opts = {"ssl_cert_reqs": ssl.CERT_NONE}      

celery_kwargs = dict(
    broker   = broker_url,
    backend  = backend_url,
)


if broker_url.startswith("rediss://"):
    celery_kwargs["broker_use_ssl"] = ssl_opts
if backend_url.startswith("rediss://"):
    celery_kwargs["redis_backend_use_ssl"] = ssl_opts   

celery_app = Celery("worker", **celery_kwargs)
