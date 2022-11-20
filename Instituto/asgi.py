"""
ASGI config for Instituto project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Instituto.settings')

# application = get_asgi_application()


import os
from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
from notifications.consumers import UserToUserRealTime


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # WebSocket chat handler
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                path("usertouser/", UserToUserRealTime.as_asgi()),
            ])
        )
    ),
    # Just HTTP for now. (We can add other protocols later.)
})
