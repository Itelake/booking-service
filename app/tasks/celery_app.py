import os
from celery import Celery

celery_app = Celery(
    "booking_worker",
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL"),
    include=["app.tasks.notification_tasks"]
)

celery_app.conf.timezone = "UTC"
celery_app.conf.enable_utc = True