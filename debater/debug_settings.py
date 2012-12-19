import settings

MIDDLEWARE_CLASSES = ['django_livejs.middleware.LivejsMiddleware','debug_toolbar.middleware.DebugToolbarMiddleware'] + settings.MIDDLEWARE_CLASSES
INSTALLED_APPS = settings.INSTALLED_APPS + ['debug_toolbar']
LIVEJS = True

INTERNAL_IPS = ('127.0.0.1',)
USE_ETAGS = True

STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static'

LIVEJS_URL = STATIC_URL+'/js/vendor/live.js' # url to live.js file