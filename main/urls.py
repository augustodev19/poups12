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
    path('processar_pagamento/', processar_pagamento, name='processar_pagamento'),
    path('criar_pagamento_com_split', criar_pagamento_com_split, name='criar_checkout_com_split')







    





    

    # Aqui estamos definindo a rota para a sua view home
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)