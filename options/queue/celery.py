from os import getenv
from celery import Celery
from celery.schedules import crontab
import eventlet

eventlet.monkey_patch(all=False, socket=True)

app = Celery(
    "options", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0"
)
app.autodiscover_tasks(["options.queue"])
app.conf.result_backend = getenv("CELERY_RESULTS_URL")
app.conf.broker_connection_retry_on_startup = True
app.conf.worker_pool = "prefork"
app.conf.worker_concurrency = 2

app.conf.beat_schedule = {
    # "update_stock_tickers_and_call_options": {
    #     "task": "options.queue.tasks.update_stock_tickers_and_call_options",
    #     "schedule": 3600,
    # },
    "spawn_update_stock_quote": {
        "task": "options.queue.tasks.spawn_update_stock_quote",
        "schedule": 60.0,
    },
    "spawn_update_options_quote": {
        "task": "options.queue.tasks.spawn_update_options_quote",
        "schedule": 60.0,
    },
}
