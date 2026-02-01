"""
Configurações Específicas para Ambiente de PRODUÇÃO
===================================================

Use este arquivo quando fizer deploy em servidor de produção real.

Como usar:
    - Configure a variável de ambiente: DJANGO_SETTINGS_MODULE=config.settings_prod
    - OU no servidor: export DJANGO_SETTINGS_MODULE=config.settings_prod
    
IMPORTANTE: Este arquivo exige variáveis de ambiente configuradas!
"""

from .settings import *
import os

# ============================================================================
# SEGURANÇA CRÍTICA
# ============================================================================

# DEBUG deve estar SEMPRE False em produção
DEBUG = False

# SECRET_KEY deve vir de variável de ambiente (obrigatório!)
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError(
        "🔴 ERRO CRÍTICO: SECRET_KEY não configurada!\n"
        "Configure a variável de ambiente SECRET_KEY antes de iniciar.\n"
        "Para gerar uma chave: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
    )

# ALLOWED_HOSTS deve ser configurado com domínios reais
ALLOWED_HOSTS_ENV = os.environ.get('ALLOWED_HOSTS', '')
if not ALLOWED_HOSTS_ENV:
    raise ValueError(
        "🔴 ERRO CRÍTICO: ALLOWED_HOSTS não configurado!\n"
        "Configure a variável de ambiente ALLOWED_HOSTS com seus domínios.\n"
        "Exemplo: ALLOWED_HOSTS=agems.ms.gov.br,www.agems.ms.gov.br"
    )
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_ENV.split(',')]

# ============================================================================
# BANCO DE DADOS - PostgreSQL (Produção)
# ============================================================================
import dj_database_url

# Lê DATABASE_URL (formato usado por Railway, Render, Heroku, etc)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,  # Conexões persistentes
            ssl_require=True   # Requer SSL
        )
    }
else:
    # Fallback: variáveis individuais
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'agems_db'),
            'USER': os.environ.get('DB_USER', 'agems_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }

# ============================================================================
# HTTPS E SSL (Obrigatório em Produção)
# ============================================================================

# Força redirecionamento para HTTPS
SECURE_SSL_REDIRECT = True

# Cookies apenas via HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HTTP Strict Transport Security (1 ano)
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Detectar HTTPS atrás de proxy (Nginx, etc)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ============================================================================
# COOKIES E SESSÕES
# ============================================================================

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 86400  # 24 horas

CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# CSRF Trusted Origins (para AJAX requests)
CSRF_TRUSTED_ORIGINS_ENV = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if CSRF_TRUSTED_ORIGINS_ENV:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS_ENV.split(',')]

# ============================================================================
# SEGURANÇA ADICIONAL
# ============================================================================

# Previne clickjacking
X_FRAME_OPTIONS = 'DENY'

# Previne MIME-type sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True

# Ativa proteção XSS do browser
SECURE_BROWSER_XSS_FILTER = True

# ============================================================================
# ARQUIVOS ESTÁTICOS E MEDIA
# ============================================================================

# WhiteNoise para servir arquivos estáticos (se não usar CDN)
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# URLs públicas (configure conforme seu CDN/storage)
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================================
# EMAIL (Produção)
# ============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# ============================================================================
# LOGGING (Produção - menos verboso, mais sério)
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',  # Apenas warnings e erros
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'ERROR',  # Apenas erros no console
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Criar diretório de logs se não existir
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# ============================================================================
# PERFORMANCE
# ============================================================================

# Cache (configure Redis se disponível)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Compressão de respostas
MIDDLEWARE += ['django.middleware.gzip.GZipMiddleware']

# ============================================================================
# MENSAGEM DE INICIALIZAÇÃO
# ============================================================================

print("🔒 [PROD] Configurações de PRODUÇÃO carregadas")
print(f"   ├─ DEBUG: {DEBUG}")
print(f"   ├─ ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"   ├─ Database: PostgreSQL")
print(f"   ├─ HTTPS: Obrigatório")
print(f"   └─ Ambiente: PRODUÇÃO")
