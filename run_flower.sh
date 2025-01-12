celery -A options.queue.celery flower --port=5555 --broker=redis://localhost:6379/0 --queues=celery
