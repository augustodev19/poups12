import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from poupsapp import consumers  # Importe seus consumers aqui se necessário

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poupsapp.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Defina rotas de websocket aqui se você tiver algum consumer
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/path/", consumers.YourConsumer.as_asgi()),
        ])
    ),
})