__author__ = 'legion'
from django.conf import settings


MPTT = False
if 'mptt' in settings.INSTALLED_APPS:
    MPTT = True


AUTOCOMPLETE = False
if 'dal' in settings.INSTALLED_APPS:
    AUTOCOMPLETE = True
