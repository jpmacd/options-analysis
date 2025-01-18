WORKER_COUNT=16 # Set the number of worker instances
for i in $(seq 1 $WORKER_COUNT); do
    WORKER_NAME=$(hostname)-worker-$i-$(uuidgen | cut -d'-' -f1)
    celery -A options.queue.celery worker -Q celery --loglevel=info --without-mingle --without-gossip -E -P gevent -n $WORKER_NAME &
done
wait
