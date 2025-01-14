WORKER_NAME=$(hostname)-worker-$(uuidgen | cut -d'-' -f1)
celery -A options.queue.celery worker -Q celery --loglevel=info -E --loglevel=INFO -P eventlet -n $WORKER_NAME
