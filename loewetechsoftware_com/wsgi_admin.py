
"""
WSGI config for loewetechsoftware_com project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
import sys

sys.path.append('/var/www/loewetechsoftware_com')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loewetechsoftware_com.settings_admin')



application = get_wsgi_application()

from django.contrib.auth.handlers.modwsgi import check_password
