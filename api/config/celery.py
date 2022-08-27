import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.config.settings')

from django.conf import settings  # noqa: E402

app = Celery('api')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
