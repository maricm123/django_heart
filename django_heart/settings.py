import os
import socket
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()  # take environment variables from .env.

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJ_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJ_DEBUG')

# Application definition
SHARED_APPS = [
    "django_tenants",
    "gym",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "debug_toolbar",
    "django_extensions",
    "channels",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

TENANT_APPS = [
    "user",
    "core",
    "training_session",
    "heart",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    'drf_spectacular',
]

INSTALLED_APPS = SHARED_APPS + [app for app in TENANT_APPS if app not in SHARED_APPS]

MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # "django_tenants.middleware.main.TenantMainMiddleware",
    # Custom middleware to cache tenant
    "django_heart.middleware.CachedTenantMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG:
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")


hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = ["127.0.0.1", "localhost"] + [
    ip[: ip.rfind(".")] + ".1" for ip in ips
]
# INTERNAL_IPS = [
#     "127.0.0.1",
#     "localhost",
#     "13.48.248.110",
# ]

####################################################################################################
# Debug toolbar
# https://django-debug-toolbar.readthedocs.io/en/stable/installation.html#internal-ips
####################################################################################################

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

ROOT_URLCONF = "django_heart.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "django_heart.wsgi.application"

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': os.environ["DJ_DB_NAME"],
        'USER': os.environ["DJ_DB_USER"],
        'PASSWORD': os.environ["DJ_DB_PASSWORD"],
        'HOST': os.environ["DJ_DB_HOST"],
        'PORT': os.environ["DJ_DB_PORT"],
    }
}

DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"

# TIME_ZONE = "UTC"
TIME_ZONE = "Europe/Belgrade"  # or "Europe/Paris"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ASGI_APPLICATION = 'django_heart.asgi.application'  # promeni u naziv svog projekta


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(os.environ.get("REDIS_HOST", "redis"), int(os.environ.get("REDIS_PORT", 6379)))],
        },
    },
}


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{os.environ.get('REDIS_HOST', 'redis')}:{os.environ.get('REDIS_PORT', 6379)}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # Optional: compression and serialization
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
        }
    }
}


AUTH_USER_MODEL = 'user.User'

ALLOWED_HOSTS = [
    '*',
    "192.168.0.4"
    "10.0.2.2",
    'heartapp.dev',
    'www.heartapp.dev',
    '13.48.248.110',
    'mygym.heartapp.dev',
]

CORS_ALLOWED_ORIGINS = [
    "http://192.168.1.50:5173",   # ako pokrećeš Vue dev server
    "http://192.168.1.50:8080",
    "http://192.168.0.2:5173",  # ako buildaš Android aplikaciju
]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ORIGIN_ALLOW_ALL = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:5173",
    "https://heartapp.dev",
    "https://*.heartapp.dev",
]

TENANT_MODEL = "gym.GymTenant"
TENANT_DOMAIN_MODEL = "gym.Domain"

PUBLIC_SCHEMA_URLCONF = "django_heart.urls"

# TENANT_COLOR_ADMIN_APPS = False

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # BASE_DIR je obično Path(__file__).resolve().parent.parent

REST_FRAMEWORK = {
    # YOUR SETTINGS
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        "rest_framework.authentication.SessionAuthentication",
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=10),  # Adjust as needed
    'REFRESH_TOKEN_LIFETIME': timedelta(days=20),  # Adjust as needed
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',  # Same as in your token header
    'AUTH_HEADER_TYPES': ('Bearer',),  # Defines how the token is passed in requests
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Your Project API',
    'DESCRIPTION': 'Your project description',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

PROJECT_NAME = "django_heart"  # currenty used for logging only
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "ignore_static": {
            "()": "core.utils.IgnoreStaticRequestsFilter"
        },
        "ignore_uvicorn_static": {
            "()": "core.utils.IgnoreStaticUvicornRequestsFilter"
        }
    },
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} | {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "filters": ["ignore_static", "ignore_uvicorn_static"],
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "app.log"),
            "formatter": "verbose",
            "filters": ["ignore_static", "ignore_uvicorn_static"],
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "WARNING",
    },
    "loggers": {
        # default for all undefined Python modules (root logger)
        "": {
            "level": "WARNING",
            "handlers": ["console"],
        },
        PROJECT_NAME: {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console", "file"],
            "level": "INFO",  # ili ERROR ako želiš još manje
            "propagate": False,
            # "filters": ["ignore_static", "ignore_uvicorn_static"],
        },
        "django.db.backends": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": True,
            # "filters": ["ignore_static", "ignore_uvicorn_static"]
        },
        "uvicorn.access": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
            # "filters": ["ignore_static", "ignore_uvicorn_static"],
        },
    },
}


# AWS
# DEFAULT_FILE_STORAGE = os.environ.get('DEFAULT_FILE_STORAGE')
# AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
# AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
# AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
# AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME")

# AWS S3 NINJA
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
AWS_STORAGE_BUCKET_NAME = "test-bucket"
AWS_S3_REGION_NAME = "us-east-1"  # može biti bilo šta
AWS_S3_ENDPOINT_URL = "http://localhost:9000"  # pokazuje na S3 Ninja
