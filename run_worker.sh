WORKER_COUNT=8  # Set the number of worker instances
for i in $(seq 1 $WORKER_COUNT); do
    WORKER_NAME=$(hostname)-worker-$i-$(uuidgen | cut -d'-' -f1)
    celery -A options.queue.celery worker -Q celery --loglevel=info -E -P eventlet -n $WORKER_NAME &
done
wait
