from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('', home_view, name='home'),
    path('lojas/', listar_lojas, name='listar_lojas'),
    path('editar_perfil/', editar_perfil, name='editar_perfil'),
    path('payment/', comprar_credito, name='payment'),
    path('loja/', loja, name='loja1'),
    path('credito_sucesso/', credito_sucesso, name='credito_sucesso'),
    path('lojas_proximas/', loja, name='loja'),
    path('loja/<int:loja_id>/', perfil_loja, name='perfil_loja'),
    path('set_location/', set_location, name='set_location'),
    path('produto/<int:id>/', detalhes_produto, name='detalhes_produto'),
    path('adicionar_ao_carrinho/<int:produto_id>/', adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('ver_carrinho/', ver_carrinho, name='ver_carrinho'),
    path('remover_do_carrinho/<int:produto_id>/', remover_do_carrinho, name='remover_do_carrinho'),
    path('checkout/', checkout, name="checkout"),
    path('criar_pagamento_checkout/', criar_pagamento_checkout, name='criar_pagamento_checkout'),
    path('pagamento/sucesso/', pagamento_sucesso, name='pagamento_sucesso'),
    path('pagamento/falha/', pagamento_falha, name='pagamento_falha'),
    path('pagamento/pendente/', pagamento_pendente, name='pagamento_pendente'),
    path('pedido_detalhe/<int:pedido_id>/', pedido_detalhe, name='pedido_detalhe'),
     path('webhook/aceitar/<int:pedido_id>/<str:token>/', aceitar_pedido, name='aceitar_pedido'),
    path('webhook/recusar/<int:pedido_id>/<str:token>/', recusar_pedido, name='recusar_pedido'),
    path('revisar/<str:acao>/<int:pedido_id>/', revisar_pedido, name='revisar_pedido'),
    path('pedido/pagamento/<int:pedido_id>/', pedido_pagamento, name='pedido_pagamento'),
    path('verificar-status-pedido/<int:pedido_id>/', verificar_status_pedido, name='verificar-status-pedido'),
    path('pagar-com-pontos/', pagar_com_pontos, name='pagar_com_pontos'),
    path('meus-pedidos/', pedidos_cliente, name='pedidos_cliente'),
    path('confirmar_compra_poups/', confirmar_compra_credito, name='confirmar_compra_credito'),
    path('webhook/', StripeWebhookView.as_view(), name='stripe_webhook'),
    
    # URL para o webhook (notificações do Mercado Pago)








    





    

    # Aqui estamos definindo a rota para a sua view home
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)