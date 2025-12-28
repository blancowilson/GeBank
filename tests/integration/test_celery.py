import pytest
from app.infrastructure.tasks.celery_app import celery_app

def test_celery_config():
    """
    Verifies that Celery is configured correctly.
    """
    assert celery_app.conf.broker_url
    assert celery_app.conf.result_backend
    assert celery_app.conf.task_serializer == "json"

def test_celery_ping_task():
    """
    Verifies that the ping task is registered.
    """
    assert "app.infrastructure.tasks.celery_app.ping" in celery_app.tasks
