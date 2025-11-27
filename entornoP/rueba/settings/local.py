from .base import *
from pathlib import Path
import os
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'db_kine',
        'USER': 'postgres',
        'PASSWORD': '1235',
        'HOST': 'localhost',
        'PORT': '5432',

    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [BASE_DIR / "static"]
# 🔹 Agrega esta línea:
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'



JAZZMIN_SETTINGS = {
    "site_title": "Proyecto Kinesiología UCN",
    "site_header": "Proyecto Kinesiología",
    "welcome_sign": "Bienvenidos al Sistema UCN",
    "site_brand": "UCN Proyecto Kinesiología",
    "site_logo": "img/imglogo_ucn.png",
    "custom_css": "css/admin_custom.css",
    "custom_js": None, 
    "icons": {
        "auth.User": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
}

FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024   # 50 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024   # 50 MB