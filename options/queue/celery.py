from os import getenv
from celery import Celery
from celery.schedules import crontab

app = Celery(
    "options", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0"
)
app.autodiscover_tasks(["options.queue"])
app.conf.result_backend = getenv("CELERY_RESULTS_URL")
app.conf.broker_connection_retry_on_startup = True
app.conf.worker_pool = "eventlet"
app.conf.worker_concurrency = 1


app.conf.beat_schedule = {
    "task-every-10-seconds": {
        "task": "tasks.my_periodic_task",
        "schedule": 10.0,  # Every 10 seconds
    },
    "task-every-day": {
        "task": "tasks.my_daily_task",
        "schedule": crontab(minute=0, hour=0),  # Every day at midnight
    },
}
