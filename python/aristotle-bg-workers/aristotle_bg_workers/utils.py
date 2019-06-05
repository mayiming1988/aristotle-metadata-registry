from celery import Task
from django.db import transaction
from django.db.models import Model
from django.apps import apps
from typing import Iterable, Mapping, Dict

from aristotle_bg_workers.celery import app


def run_task_on_commit(task: Task, args: Iterable = [], kwargs: Mapping = {}):
    """Run a celery task after the next database commit (if we are in a transaction)"""
    transaction.on_commit(lambda: task.delay(*args, **kwargs))


def run_task_by_name_on_commit(task: str, args: Iterable = [], kwargs: Mapping = {}):
    """
    Run a celery task by name after the next database commit (if we are in a transaction)
    The function above is preffered, only use this one if you can't import the task
    """
    transaction.on_commit(lambda: app.send_task(task, args, kwargs))


def lookup_model(data: Dict) -> Model:
    """Lookup model from dict containing app label and model name"""
    return apps.get_model(data['app_label'], data['model_name'])
