"""
Flask wrapper for Django WSGI application
"""
import os
import sys

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Import Django
import django
django.setup()

# Get Django WSGI application
from django.core.wsgi import get_wsgi_application
django_app = get_wsgi_application()

# Create Flask app as wrapper
from flask import Flask, request
from werkzeug.wrappers import Response

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def catch_all(path):
    """Forward all requests to Django"""
    environ = request.environ
    response_data = []
    
    def start_response(status, headers):
        response_data.append((status, headers))
    
    # Call Django app
    result = django_app(environ, start_response)
    
    # Build Flask response
    if response_data:
        status, headers = response_data[0]
        response = Response(b''.join(result), status=status.split()[0])
        for header, value in headers:
            response.headers[header] = value
        return response
    
    return Response(b''.join(result))
