from celery import Celery
from celery.schedules import crontab


celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

celery_app.autodiscover_tasks(["app.celery.tasks"])

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


celery_app.conf.beat_schedule = {
    "delete-old-logs-daily": {
        "task": "app.celery.tasks.delete_old_logs",  # <-- Full dotted path is safest
        "schedule": crontab(hour=0, minute=0),
    },
}


celery_app.conf.beat_schedule.update({
    "monthly-summary": {
        "task": "app.reports.generate_monthly_summary",
        "schedule": crontab(hour=2, minute=0, day_of_month=1),
        "args": ({"year": None, "month": None, "threshold_percentage": 15.0},)
    }
})

