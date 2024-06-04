import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import poupsapp.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poupsapp.settings')

# Inicialize o Django
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        (
            URLRouter(
                poupsapp.routing.websocket_urlpatterns
            )
        )
    ),
})