from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/pedidos/', consumers.PedidoConsumer.as_asgi()),
]