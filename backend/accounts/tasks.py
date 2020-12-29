from django.core import management

from theraq.celery import app as celery_app


@celery_app.task
def clearsessions():
    management.call_command('clearsessions')
