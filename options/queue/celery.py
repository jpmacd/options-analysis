from os import getenv
from celery import Celery

app = Celery(
    "options", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0"
)
app.autodiscover_tasks(["options.queue.tasks"])
app.conf.result_backend = getenv("CELERY_RESULTS_URL")
app.conf.broker_connection_retry_on_startup = True
app.conf.worker_pool = "eventlet"
app.conf.worker_concurrency = 1
