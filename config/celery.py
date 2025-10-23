import os
from celery import Celery

# Define o módulo de configurações padrão do Django para o programa 'celery'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('agems_regulatorio')

# Usando uma string aqui significa que o worker não precisa serializar
# o objeto de configuração para processos filhos.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carrega módulos de tarefas de todas as apps Django registradas.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
