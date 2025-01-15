WORKER_COUNT=1  # Set the number of worker instances
for i in $(seq 1 $WORKER_COUNT); do
    WORKER_NAME=$(hostname)-worker-$i-$(uuidgen | cut -d'-' -f1)
    celery -A options.queue.celery worker -Q celery --loglevel=debug -E -P eventlet -n $WORKER_NAME &
done
wait
