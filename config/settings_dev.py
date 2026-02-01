"""
Configurações Específicas para Ambiente de DESENVOLVIMENTO
==========================================================

Use este arquivo quando estiver desenvolvendo localmente no seu computador.

Como usar:
    python manage.py runserver --settings=config.settings_dev

Ou configure a variável de ambiente:
    set DJANGO_SETTINGS_MODULE=config.settings_dev
"""

from .settings import *

# ============================================================================
# DEBUG E DESENVOLVIMENTO
# ============================================================================
DEBUG = True

# Permite acesso de qualquer host em desenvolvimento
ALLOWED_HOSTS = ['*']

# ============================================================================
# BANCO DE DADOS - SQLite (Simples para dev)
# ============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ============================================================================
# SEGURANÇA - RELAXADA (apenas para dev!)
# ============================================================================
# ❌ NÃO usar essas configurações em produção!

SECRET_KEY = 'django-insecure-dev-key-only-for-local-development'

# Desabilitar redirecionamento HTTPS
SECURE_SSL_REDIRECT = False

# Cookies podem ser enviados via HTTP (localhost)
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Sem HSTS em desenvolvimento
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# ============================================================================
# EMAIL - Console Backend (emails aparecem no terminal)
# ============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ============================================================================
# LOGGING - Mais verboso para debug
# ============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ============================================================================
# FERRAMENTAS DE DESENVOLVIMENTO (opcional)
# ============================================================================
# Se você instalar django-debug-toolbar:
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
# INTERNAL_IPS = ['127.0.0.1']

print("🔧 [DEV] Configurações de DESENVOLVIMENTO carregadas")
print(f"   ├─ DEBUG: {DEBUG}")
print(f"   ├─ Database: SQLite")
print(f"   └─ Ambiente: LOCAL")
