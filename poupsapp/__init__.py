from __future__ import absolute_import, unicode_literals

# Certifique-se de que este código está no __init__.py da pasta principal
from .celery import app as celery_app

__all__ = ('celery_app',)