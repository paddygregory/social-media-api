from celery import Celery
import os

broker_url = os.getenv("REDIS_BROKER_URL")
backend_url = os.getenv("REDIS_BACKEND_URL", broker_url)  # fallback to same

# Inject Redis TLS options explicitly
broker_use_ssl = {
    "ssl_cert_reqs": "none"  # Use "required" or "optional" for stricter configs
}
backend_use_ssl = {
    "ssl_cert_reqs": "none"
}

celery_app = Celery(
    "worker",
    broker=broker_url,
    backend=backend_url,
    broker_use_ssl=broker_use_ssl if broker_url.startswith("rediss://") else None,
    backend_use_ssl=backend_use_ssl if backend_url.startswith("rediss://") else None
)