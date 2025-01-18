from os import getenv
from celery import Celery
from celery.schedules import crontab

app = Celery(
    "options",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

app.autodiscover_tasks(["options.queue"])
app.conf.result_backend = getenv("CELERY_RESULTS_URL", "redis://localhost:6379/1")
app.conf.broker_connection_retry_on_startup = True
app.conf.worker_pool = "gevent"
app.conf.worker_concurrency = 2

app.conf.beat_schedule = {
    # "update_stock_tickers_and_call_options": {
    #     "task": "options.queue.tasks.update_stock_tickers_and_call_options",
    #     "schedule": crontab(minute=0, hour="4"),
    # },
    "spawn_update_stock_quote": {
        "task": "options.queue.tasks.spawn_update_stocks_quote",
        "schedule": 180.00,
    },
    "spawn_update_options_quote": {
        "task": "options.queue.tasks.spawn_update_options_quote",
        "schedule": 180.0,
    },
}
