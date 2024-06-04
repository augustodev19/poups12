from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/pedidos/<int:user_id>/', consumers.PedidoConsumer.as_asgi()),
]