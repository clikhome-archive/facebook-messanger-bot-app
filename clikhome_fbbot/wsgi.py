"""
WSGI config for fbbot project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clikhome_fbbot.settings')
# os.environ.setdefault('DJANGO_CONFIGURATION', 'Dev')
from configurations.wsgi import get_wsgi_application
from dj_static import Cling

application = Cling(get_wsgi_application())
