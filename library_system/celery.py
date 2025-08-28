import os

from celery.schedules import crontab

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')

app = Celery('library_system')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'loan-over-due-email-task': {
        'task': 'library.tasks.check_overdue_loans',
        'schedule': crontab(minute=0, hour=0)  # runs daily at midnight
        # 'schedule': 1.0,  # to test task, it will run every second
    },
}
