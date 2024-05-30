"""
Django settings for poupsapp project.

Generated by 'django-admin startproject' using Django 5.0.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
import json
from celery.schedules import crontab

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

LOGOUT_REDIRECT_URL = 'home'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587  # ou 465 para SSL
EMAIL_USE_TLS = True  # ou EMAIL_USE_SSL = True para SSL
EMAIL_HOST_USER = 'augusto.dataanalysis@gmail.com'
EMAIL_HOST_PASSWORD = 'muel jqer xnpw slqq'
DEFAULT_FROM_EMAIL = 'augusto.webdeveloping@gmail.com'
PASSWORD_RESET_EMAIL_SUBJECT = 'Redefinição de Senha do Nosso Site'
PASSWORD_RESET_TEMPLATE_NAME = 'core/mudarSenha.html'
LOGIN_URL = 'login'


CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Sao_Paulo'
CELERY_RESULT_BACKEND = CELERY_BROKER_URL


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-1q$$n3hh=h1f*n8i2lwjivc2dz2_ics324t0&5i7k10nmd3x69'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['poupecomprando.onrender.com.br', '8f94-2804-5854-180-500-431-e1d2-a81a-dadb.ngrok-free.app', 'a3d0-2804-5854-180-500-4159-968a-12d0-ca20.ngrok-free.app', '8321-2804-5854-180-500-b876-f01f-7ecb-9c67.ngrok-free.app', 'localhost', 'f5fa-2804-5854-180-500-645b-d77b-26b9-38af.ngrok-free.app', 'c02e-2804-5854-180-500-431-e1d2-a81a-dadb.ngrok-free.app', '0106-2804-5854-180-500-5524-f3c2-b2f6-4584.ngrok-free.app', '80b7-2804-5854-180-500-bc88-711e-50da-3a63.ngrok-free.app', 'e131-2804-5854-180-500-23-9b99-2a92-5f03.ngrok-free.app', 'poupecomprando.com.br', 'poups12.onrender.com', '127.0.0.1', 'poupecomprando.com', 'www.poupecomprando.com', 'www.poupecomprando.com.br']
CSRF_TRUSTED_ORIGINS = ['https://poupecomprando.com.br/*', 'https://f5fa-2804-5854-180-500-645b-d77b-26b9-38af.ngrok-free.app/*', 'https://a3d0-2804-5854-180-500-4159-968a-12d0-ca20.ngrok-free.app/*', 'https://8321-2804-5854-180-500-b876-f01f-7ecb-9c67.ngrok-free.app/*', 'https://8f94-2804-5854-180-500-431-e1d2-a81a-dadb.ngrok-free.app/*', 'https://c02e-2804-5854-180-500-431-e1d2-a81a-dadb.ngrok-free.app/*', 'https://0106-2804-5854-180-500-5524-f3c2-b2f6-4584.ngrok-free.app/*', 'http://localhost:8976/*', 'https://80b7-2804-5854-180-500-bc88-711e-50da-3a63.ngrok-free.app/*', 'https://e131-2804-5854-180-500-23-9b99-2a92-5f03.ngrok-free.app/*', 'http://localhost/*', 'https://poupecomprando.com/*', 'https://poups12.onrender.com/*', 'https://www.poupecomprando.com/*', 'https://www.poupecomprando.com.br/*']
    

LOGOUT_REDIRECT_URL = 'home'


CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/1'),  # substitua pelo seu endereço e porta do Redis
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Opcional: Definir cache de sessão
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

#LOGGING = {
#    'version': 1,
#    'disable_existing_loggers': False,
#    'handlers': {
#        'console': {
#            'level': 'DEBUG',
#            'class': 'logging.StreamHandler',
#        },
#        'file': {
#            'level': 'DEBUG',
#            'class': 'logging.FileHandler',
#            'filename': os.path.join(BASE_DIR, 'debug.log'),
#        },
#    },
#    'loggers': {
#        'django': {
#            'handlers': ['console', 'file'],
#            'level': 'DEBUG',
#            'propagate': True,
#        },
#        'celery': {
#            'handlers': ['console', 'file'],
#            'level': 'DEBUG',
#            'propagate': True,
#        },
#    },
#}

AUTH_USER_MODEL = 'usuarios.CustomUser'
MERCADO_PAGO_SECRET_KEY = '6947fa76368c6d59aae0f9934e64322507934292126d14931dd72ed35dc1d843'
MERCADO_PAGO_ACCESS_TOKEN = 'APP_USR-59977399911432-110210-7d39b5cafcec9b58b960954a9d495897-1323304242'
STRIPE_WEBHOOK_SECRET = 'whsec_IMHkfsYp2o9UZ0lvZ73uBGVWC9gNAwrp'
# Application definition

INSTALLED_APPS = [

    'jazzmin',
    'storages',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'usuarios',
    'main',
    'django_redis',
    'django_celery_results',
    #'channels',
    #'chat'
]

#ASGI_APPLICATION = 'chat.asgi.application'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'usuarios.backends.EmailAuthenticationBackend',  # Seu backend personalizado
]

STRIPE_PUBLIC_KEY = 'pk_test_51PHMq7CFqCCeinfhPzL8Rn37toV7ktSXAajyVDiZK6KS0J9mmEcpWwzges2ETl4NiPpQyMz2krzeOkaeMmJTmyIL00XRi0wfcD'
STRIPE_SECRET_KEY = 'sk_test_51PHMq7CFqCCeinfhM7MDQ086AzXSszH5S6SbmHzNo2GnysN3AfZvJeVYzD8myLBvTHdCWqFQRfxTfFciwf2DFc3m00k6zHcMzu'

ROOT_URLCONF = 'poupsapp.urls'
MY_BASE_URL = 'https://poupecomprando.com.br'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'poupsapp/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
WSGI_APPLICATION = 'poupsapp.wsgi.application'
# Função para carregar as credenciais do Google Cloud
#def load_gcs_credentials():
#    credentials_path = os.path.join(BASE_DIR, 'credentials', 'phonic-realm-411312-5ceef67c1a57.json')
#    if 'GOOGLE_APPLICATION_CREDENTIALS_JSON' in os.environ:
#        os.makedirs(os.path.dirname(credentials_path), exist_ok=True)
#        with open(credentials_path, 'w') as f:
#            f.write(os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON'])
#    return credentials_path
#
## Definir a variável de ambiente para apontar para o arquivo JSON
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = load_gcs_credentials()
#
#
#DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
#GS_BUCKET_NAME = 'poupecomprando'

# Remover ou comentar a linha de ACL legado
# GS_DEFAULT_ACL = 'publicRead'

# Opcional: Configurar cache control
#GS_FILE_OVERWRITE = False
#GS_CACHE_CONTROL = 'max-age=86400'

# URL base para acessar os arquivos
#MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/'
# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
#}

# Define BASE_DIR

# Configuração do banco de dados PostgreSQL usando variáveis de ambiente
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'poupecomprando',
        'USER': 'poupecomprando_user',
        'PASSWORD': 'uk4G84RyR2veH6hCuf5A9uLnKYnWdWCM',
        'HOST': 'dpg-cn6udpol6cac73bqelfg-a.oregon-postgres.render.com',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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




# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/
LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'


USE_I18N = True

USE_TZ = True



WSGI_APPLICATION = 'poupsapp.wsgi.application'

# Função para carregar as credenciais do Google Cloud
def load_gcs_credentials():
    credentials_path = os.path.join(BASE_DIR, 'credentials', 'trusty-legend-424903-n8-6703dacb6a5f.json')
    if 'GOOGLE_APPLICATION_CREDENTIALS_JSON' in os.environ:
        os.makedirs(os.path.dirname(credentials_path), exist_ok=True)
        with open(credentials_path, 'w') as f:
            f.write(os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON'])
    return credentials_path

# Definir a variável de ambiente para apontar para o arquivo JSON
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = load_gcs_credentials()

DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = 'poupecomprando12'

# Remover ou comentar a linha de ACL legado
GS_DEFAULT_ACL = 'publicRead'

# Opcional: Configurar cache control
GS_FILE_OVERWRITE = False
GS_CACHE_CONTROL = 'max-age=86400'

# URL base para acessar os arquivos
MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/'

# Configuração de arquivos estáticos
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'poupsapp/static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')



JAZZMIN_SETTINGS = {
    
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "PoupeComprando",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "PoupeComprando",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "PoupeComprando",

    # Logo to use for your site, must be present in static files, used for brand on top left
    "site_logo": None,
    
    # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
    "login_logo": None,

    # Logo to use for login form in dark themes (defaults to login_logo)
    "login_logo_dark": None,

    # CSS classes that are applied to the logo above
    "site_logo_classes": None,

    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    "site_icon": True,

    # Welcome text on the login screen
    "welcome_sign": "Admin PoupeComprando",

    # Copyright on the footer
    "copyright": "PoupeComprando",

    # List of model admins to search from the search bar, search bar omitted if excluded
    # If you want to use a single search field you dont need to use a list, you can use a simple string 
    "search_model": ["auth.User", "auth.Group"],

    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
    "user_avatar": None,

    ############
    # Top Menu #
    ############

    # Links to put along the top menu
    "topmenu_links": [

        # Url that gets reversed (Permissions can be added)
        {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},

        # external url that opens in a new window (Permissions can be added)
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},

        # model admin to link to (Permissions checked against model)
        {"model": "auth.User"},

        # App with dropdown menu to all its models pages (Permissions checked against models)
        {"app": "books"},
    ],

    #############
    # User Menu #
    #############

    # Additional links to include in the user menu on the top right ("app" url type is not allowed)
    "usermenu_links": [
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        {"model": "auth.user"}
    ],

    #############
    # Side Menu #
    #############

    # Whether to display the side menu
    "show_sidebar": True,

    # Whether to aut expand the menu
    "navigation_expanded": True,

    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": [],

    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [],

    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": ["auth", "books", "books.author", "books.book"],

    # Custom links to append to app groups, keyed on app name
    "custom_links": {
        "books": [{
            "name": "Make Messages", 
            "url": "make_messages", 
            "icon": "fas fa-comments",
            "permissions": ["books.view_book"]
        }]
    },

    # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,5.0.10,5.0.11,5.0.12,5.0.13,5.0.2,5.0.3,5.0.4,5.0.5,5.0.6,5.0.7,5.0.8,5.0.9,5.1.0,5.1.1,5.2.0,5.3.0,5.3.1,5.4.0,5.4.1,5.4.2,5.13.0,5.12.0,5.11.2,5.11.1,5.10.0,5.9.0,5.8.2,5.8.1,5.7.2,5.7.1,5.7.0,5.6.3,5.5.0,5.4.2
    # for the full list of 5.13.0 free icon classes
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": True,

    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": False,
    "custom_js": True,
    # Whether to link font from fonts.googleapis.com (use custom_css to supply font otherwise)
    "use_google_fonts_cdn": True,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": True,

    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    # Add a language dropdown into the admin
    "language_chooser": False,
    
    
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": True,
    "brand_small_text": False,
    "brand_colour": "navbar-light",
    "accent": "accent-navy",
    "navbar": "navbar-cyan navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-light-info",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": True,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}