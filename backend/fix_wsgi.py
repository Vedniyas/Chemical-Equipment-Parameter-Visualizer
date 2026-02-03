import os

# Define path to wsgi.py
wsgi_path = os.path.join("backend", "wsgi.py")

# The correct content for wsgi.py
wsgi_content = """
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = get_wsgi_application()
"""

print(f"Writing correct configuration to {wsgi_path}...")
with open(wsgi_path, "w") as f:
    f.write(wsgi_content)

print("SUCCESS: backend/wsgi.py restored!")