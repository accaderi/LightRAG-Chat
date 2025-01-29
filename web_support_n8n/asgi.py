"""
ASGI config for web_support_n8n project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

"""
ASGI config for web_support_n8n project.
"""

import os
# Set the settings module before importing anything else
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_support_n8n.settings')

from django.core.asgi import get_asgi_application

# Get the ASGI application
application = get_asgi_application()

# async def application(scope, receive, send):
#     if scope['type'] == 'http':
#         await django_asgi_app(scope, receive, send)
#     else:
#         raise NotImplementedError(f"Unknown scope type {scope['type']}")
