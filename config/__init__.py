# Isso garantirá que o app Celery seja sempre importado quando o Django iniciar
from .celery import app as celery_app

__all__ = ('celery_app',)
