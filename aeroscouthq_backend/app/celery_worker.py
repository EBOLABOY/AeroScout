from celery import Celery
from app.core.config import settings

# Initialize Celery
# The first argument is the name of the current module, which is used for naming tasks.
# The 'broker' and 'backend' arguments specify the URLs for the message broker and result backend.
# The 'include' argument is a list of modules to import when the worker starts.
# This is where your task modules should be listed.
celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        'app.core.tasks', # Points to the module where task functions will be defined
        # Add other task modules here if needed in the future
    ]
)

# Optional configuration settings
# Example: Set a default queue and route tasks starting with 'app.core.tasks.' to it.
celery_app.conf.task_routes = {
    "app.core.tasks.*": "main-queue"
}

# Configure JSON serialization to fix EncodeError issues with datetime objects
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    # Additional settings for better reliability
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

if __name__ == '__main__':
    # This allows running the worker directly using: python -m app.celery_worker worker --loglevel=info
    # Note: Typically, you'd run Celery worker from the command line using the celery command.
    # Example: celery -A app.celery_worker worker --loglevel=info -Q main-queue
    celery_app.start()