from django.urls import re_path
from .consumers import PedidoConsumer

websocket_urlpatterns = [
    re_path(r'ws/pedidos/(?P<loja_id>\w+)/$', PedidoConsumer.as_asgi()),
]