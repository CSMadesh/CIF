import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ixova.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Vercel needs this named 'app'
app = application
