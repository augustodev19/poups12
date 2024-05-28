from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poupsapp.settings')

app = Celery('poupsapp')

# Using a string here means the worker does not have to
# pickle the object when using Windows.
app.conf.update(timezone = 'America/Sao_Paulo')
app.config_from_object(settings, namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')