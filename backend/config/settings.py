from pathlib import Path
from datetime import timedelta
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────────────────────────
# SEGURIDAD CRÍTICA
# ─────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError('SECRET_KEY no está definido en las variables de entorno')

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()]

# ─────────────────────────────────────────────────────────────────
# APLICACIONES
# ─────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.microsoft',
    # Local
    'core',
    'curriculum',
    'students',
    'courses',
    'enrollments',
    'grades',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    # Protege /system-admin/ — debe ir DESPUÉS de AuthenticationMiddleware
    'core.middleware.AdminAccessMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ─────────────────────────────────────────────────────────────────
# BASE DE DATOS — con pool de conexiones
# ─────────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':     os.environ.get('DB_NAME', 'auth_db'),
        'USER':     os.environ.get('DB_USER', 'university_admin'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST':     os.environ.get('DB_HOST', 'localhost'),
        'PORT':     os.environ.get('DB_PORT', '5432'),
        # Reutiliza conexiones por 60 s dentro de cada worker Gunicorn
        'CONN_MAX_AGE':     int(os.environ.get('DB_CONN_MAX_AGE', '60')),
        'CONN_HEALTH_CHECKS': True,
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000',  # 30 s máx por query
        },
    }
}

AUTH_USER_MODEL = 'core.CustomUser'

# ─────────────────────────────────────────────────────────────────
# CACHÉ — Redis (evita llamadas repetidas al validar tokens)
# ─────────────────────────────────────────────────────────────────
REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS':          'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 3,
            'SOCKET_TIMEOUT':         3,
            # Si Redis no responde, continúa sin caché (no crashea)
            'IGNORE_EXCEPTIONS':      True,
        },
        'KEY_PREFIX': 'auth',
        'TIMEOUT':    300,  # 5 minutos por defecto
    }
}

# Sesiones en Redis (más rápido que PostgreSQL)
SESSION_ENGINE      = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE  = 28800   # 8 horas
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# ─────────────────────────────────────────────────────────────────
# DJANGO-ALLAUTH
# ─────────────────────────────────────────────────────────────────
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'core.auth_backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_LOGIN_METHODS         = {'email'}
ACCOUNT_EMAIL_REQUIRED        = True
ACCOUNT_USERNAME_REQUIRED     = False
ACCOUNT_EMAIL_VERIFICATION    = 'none'
# En desarrollo local usamos http; en producción (dominio real) cambiar a 'https'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'

SOCIALACCOUNT_AUTO_SIGNUP    = True
SOCIALACCOUNT_LOGIN_ON_GET   = True
SOCIALACCOUNT_ADAPTER        = 'core.adapters.AspirantSocialAccountAdapter'
# Permitir callback OAuth desde localhost sin verificación de origin estricta
SOCIALACCOUNT_STORE_TOKENS   = False

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
            'secret':    os.environ.get('GOOGLE_CLIENT_SECRET', ''),
            'key': '',
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
    },
    'microsoft': {
        'APP': {
            'client_id': os.environ.get('MICROSOFT_CLIENT_ID', ''),
            'secret':    os.environ.get('MICROSOFT_CLIENT_SECRET', ''),
            'key': '',
        },
        'TENANT': 'common',
        'SCOPE': ['User.Read'],
        'AUTH_PARAMS': {'response_type': 'code'},
    },
}

# ─────────────────────────────────────────────────────────────────
# CORS — solo orígenes explícitos en producción
# ─────────────────────────────────────────────────────────────────
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS  = False
    CORS_ALLOWED_ORIGINS    = [
        o.strip() for o in os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost').split(',')
        if o.strip()
    ]
    CORS_ALLOW_CREDENTIALS  = True

# Orígenes de confianza para CSRF (necesario para callbacks OAuth con nginx proxy)
CSRF_TRUSTED_ORIGINS = [
    'http://localhost',
    'http://127.0.0.1',
    *[o.strip() for o in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if o.strip()],
]

# Cabecera que Django usa para detectar el esquema real detrás del proxy nginx
USE_X_FORWARDED_HOST  = True
SECURE_PROXY_SSL_HEADER = None   # No forzar HTTPS en desarrollo

# ─────────────────────────────────────────────────────────────────
# DJANGO REST FRAMEWORK
# ─────────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/minute',
        'user': '300/minute',
        'anon_registration': '10/hour',
        'anon_login': '20/hour',
    },
}

REST_FRAMEWORK_THROTTLE = {
    'DEFAULT_THROTTLE_CLASSES': [],
    'DEFAULT_THROTTLE_RATES': {
        'anon_registration': '10/hour',
        'anon_login': '20/hour',
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS':  False,
    'ALGORITHM':              'HS256',
    'AUTH_HEADER_TYPES':      ('Bearer',),
}

# ─────────────────────────────────────────────────────────────────
# SEGURIDAD ADICIONAL (activa cuando DEBUG=False)
# ─────────────────────────────────────────────────────────────────
if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF     = True
    SECURE_BROWSER_XSS_FILTER       = True
    X_FRAME_OPTIONS                  = 'DENY'
    SECURE_REFERRER_POLICY          = 'strict-origin-when-cross-origin'
    SESSION_COOKIE_SECURE            = True   # Solo HTTPS
    CSRF_COOKIE_SECURE               = True   # Solo HTTPS
    # SECURE_SSL_REDIRECT            = True   # Descomentar cuando tengas SSL en nginx

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─────────────────────────────────────────────────────────────────
# INTERNACIONALIZACIÓN
# ─────────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'es-ve'
TIME_ZONE     = 'America/Caracas'
USE_I18N      = True
USE_TZ        = True

# ─────────────────────────────────────────────────────────────────
# ARCHIVOS ESTÁTICOS Y MEDIA
# ─────────────────────────────────────────────────────────────────
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL   = '/media/'
MEDIA_ROOT  = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─────────────────────────────────────────────────────────────────
# LOGGING — estructurado, útil en producción
# ─────────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class':     'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level':    os.environ.get('LOG_LEVEL', 'INFO').upper(),
    },
    'loggers': {
        'django.security': {
            'handlers':  ['console'],
            'level':     'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers':  ['console'],
            'level':     'WARNING',
            'propagate': False,
        },
    },
}

# ─────────────────────────────────────────────────────────────────
# URLS DE AUTENTICACIÓN
# ─────────────────────────────────────────────────────────────────
LOGIN_URL          = '/'
LOGIN_REDIRECT_URL = '/home/'
LOGOUT_REDIRECT_URL = '/'

# ─────────────────────────────────────────────────────────────────
# URLS INTER-SERVICIOS
# ─────────────────────────────────────────────────────────────────
STUDENTS_SERVICE_URL = os.environ.get('STUDENTS_SERVICE_URL', 'http://students_service:8001')

# ─────────────────────────────────────────────────────────────────
# EMAIL — SMTP configurable desde variables de entorno
# Si EMAIL_HOST no está definido, usa el backend de consola (solo imprime
# los emails en los logs del servidor — útil para desarrollo).
# Para producción, definir EMAIL_HOST, EMAIL_HOST_USER y EMAIL_HOST_PASSWORD
# en el archivo .env o en las variables de entorno del contenedor.
# ─────────────────────────────────────────────────────────────────
_email_host = os.environ.get('EMAIL_HOST', '')

if _email_host:
    # SMTP real configurado
    EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST          = _email_host
    EMAIL_PORT          = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_USE_TLS       = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_USE_SSL       = os.environ.get('EMAIL_USE_SSL', 'False') == 'True'
    EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
    DEFAULT_FROM_EMAIL  = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'noreply@upel.edu.ve')
else:
    # Sin SMTP → imprime emails en consola (logs del contenedor)
    EMAIL_BACKEND      = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'noreply@upel.edu.ve'

EMAIL_SUBJECT_PREFIX = '[UPEL BasePNew] '
