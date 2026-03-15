import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_heart.settings')

app = Celery('django_heart')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

from core.tasks import send_training_session_report_email_task

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
