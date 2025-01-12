from os import getenv
from celery import Celery

app = Celery("tasks", broker=getenv("CELERY_BROKER_URL"))

app.conf.result_backend = getenv("CELERY_RESULTS_URL")
app.conf.broker_connection_retry_on_startup = True
