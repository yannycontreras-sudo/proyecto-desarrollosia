"""
ASGI config for rueba project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

<<<<<<< HEAD
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prueba.settings')
=======
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rueba.settings')
>>>>>>> parent of 41cc053 (base nueva template)

application = get_asgi_application()
