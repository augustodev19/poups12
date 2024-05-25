from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Defina o módulo de configurações padrão do Django para o Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poupsapp.settings')

app = Celery('poupsapp')

# Usar uma string aqui significa que o worker não precisa serializar
# a configuração do objeto para filhos.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carregar tasks do módulo 'tasks.py' em cada aplicativo do Django.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')