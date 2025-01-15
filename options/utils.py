from datetime import datetime


def convert_timestamp(timestamp: str) -> str:
    ts = int(timestamp)
    seconds = ts // 1_000_000_000
    microseconds = (ts % 1_000_000_000) // 1000
    local_time = (
        datetime.fromtimestamp(seconds)
        .replace(microsecond=microseconds)
        .strftime("%Y-%m-%d %H:%M:%S.%f")
    )
    return local_time


from celery.result import AsyncResult
from celery import current_app


def get_task_queue_status():
    app = current_app._get_current_object()
    inspector = app.control.inspect()

    queued_tasks = inspector.reserved() or {}
    active_tasks = inspector.active() or {}

    total_queued = (
        sum(len(tasks) for tasks in queued_tasks.values()) if queued_tasks else 0
    )
    total_active = (
        sum(len(tasks) for tasks in active_tasks.values()) if active_tasks else 0
    )

    completed_tasks = 0
    task_ids = []
    for task_id in task_ids:
        result = AsyncResult(task_id)
        if result.status == "SUCCESS":
            completed_tasks += 1

    total_tasks = total_queued + total_active + completed_tasks
    percent_complete = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

    return {
        "queued": total_queued,
        "active": total_active,
        "completed": completed_tasks,
        "percent_complete": percent_complete,
    }
