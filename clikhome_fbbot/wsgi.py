"""
WSGI config for fbbot project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clikhome_fbbot.settings')
# os.environ.setdefault('DJANGO_CONFIGURATION', 'Dev')

application = get_wsgi_application()
