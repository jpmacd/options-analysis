from options.queue.celery import app
import logging


@app.task
def add(x, y):
    logging.info(f"Adding {x} + {y}")
    result = x + y
    logging.info(f"Result: {result}")
    return result
