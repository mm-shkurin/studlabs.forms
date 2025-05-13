from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv
load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost","127.0.0.1","mm-shkurin-absoluteomsk-api-7aca.twc1.net","absoluteomsk.ru" ]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000", 
    "http://127.0.0.1:8000", 
    "https://mm-shkurin-absoluteomsk-api-7aca.twc1.net",
    "https://absoluteomsk.ru"
]

CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000','https://mm-shkurin-absoluteomsk-api-7aca.twc1.net',"https://absoluteomsk.ru"  ]
CSRF_COOKIE_SECURE = False
CSRF_USE_SESSIONS = False

CSRF_TRUSTED_ORIGINS = [
'https://mm-shkurin-absoluteomsk-api-7aca.twc1.net',
"https://absoluteomsk.ru" ,
'http://localhost:8000',
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_yasg',
    'djoser',
    'corsheaders',
    'channels',
    'user',
    'forms'
]
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
         'rest_framework_simplejwt.authentication.JWTAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.AllowAny',
    ]
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware'
]

ROOT_URLCONF = 'LabForm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'LabForm.wsgi.application'
ASGI_APPLICATION = 'LabForm.asgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Internationalization
LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


# Static files & media (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = '/LabForm/staticfiles/'
'''STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    '/usr/local/lib/python3.11/site-packages/rest_framework/static',
]'''

MEDIA_URL = '/media/'
MEDIA_ROOT = '/LabForm/media/'
#MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Для разработки
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# User auth with telegram & email(djoser)
AUTH_USER_MODEL = 'user.User'
 
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Обычная аутентификация (email + пароль)
    'user.authentication.TelegramAuthBackend',  # Аутентификация по Telegram ID
]

DJOSER = {
    'LOGIN_FIELD': 'email',
    'USER_CREATE_PASSWORD_RETYPE': True,
    'SEND_ACTIVATION_EMAIL': False,
    'PASSWORD_RESET_CONFIRM_URL': 'reset-password-confirm/{uid}/{token}',
    'SERIALIZERS': {
        'user_create': 'user.serializers.RegisterSerializer',
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}
#Email settings for djoser
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 465
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT-токен в формате: Bearer <token>'
        }
    },
    'USE_SESSION_AUTH': False,
    'DEFAULT_FIELD_INSPECTORS': [
        'drf_yasg.inspectors.CamelCaseJSONFilter',
        'drf_yasg.inspectors.InlineSerializerInspector',
        'drf_yasg.inspectors.RelatedFieldInspector',
        'drf_yasg.inspectors.ChoiceFieldInspector',
        'drf_yasg.inspectors.FileFieldInspector',
        'drf_yasg.inspectors.DictFieldInspector',
        'drf_yasg.inspectors.JSONFieldInspector',
        'drf_yasg.inspectors.HiddenFieldInspector',
        'drf_yasg.inspectors.RecursiveFieldInspector',
        'drf_yasg.inspectors.SerializerMethodFieldInspector',
        'drf_yasg.inspectors.SimpleFieldInspector',
        'drf_yasg.inspectors.StringDefaultFieldInspector',
    ],
}