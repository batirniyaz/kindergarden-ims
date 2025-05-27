from app.celery.tasks import test_task
from app.celery.celery_app import celery_app

from fastapi import APIRouter

router = APIRouter()


@router.post("/run-task")
def run_task(name: str):
    task = test_task.delay(name)
    return {"task_id": task.id}


@router.get("/task-status/{task_id}")
def get_status(task_id: str):

    task = celery_app.AsyncResult(task_id)
    return {"status": task.status, "result": task.result}