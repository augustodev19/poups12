from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('registrarCliente/', registerCliente, name='registerCliente'),
    path('registrarFamilia/', registerFamilia, name='registerFamilia'),
    path('registrarLoja/', registerLoja, name='registerLoja'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('entrar/', user_login, name='login'),
    path('editar_loja/', editar_loja, name='editar_loja'),
    path('editar_catalogo/', catalogo, name='catalogo'),
    path('alterar_entrega/', entrega, name='entrega'),
    path('update_capa/', update_capa, name='update_capa'),
    path('editar_geral/', editar_geral, name='editar_geral'),
    path('criar_produto/', criar_produto, name='criar_produto'),
    path('remover_produto/<int:produto_id>/', remover_produto, name='remover_produto'),
    path('buscar_produto/<int:produto_id>/', buscar_produto, name='buscar_produto'),
    path('editar_produto/', editar_produto, name='editar_produto'),
    path('tipo_cliente/', tipo_cliente, name='tipoCliente'),
    path('criar_subperfil/', create_subperfil, name='criarSubperfil'),
    path('perfil_familia/', perfil_familia, name='perfil_familia'),
    path('tipo_perfil/', tipo_perfil, name='tipoPerfil'),
    path('meu_perfil/', perfil_usuario, name='perfil_usuario'),
    path('ajax/sales-by-month/', get_sales_by_month, name='sales-by-month'),
    path('pedidos-loja/', ver_pedidos_loja, name='ver_pedidos_loja'),
    path('criar-pedido_loja/', criar_pedido_loja, name='criar_pedido_loja'),
    path('categoria/remover/<int:categoria_id>/', remover_categoria, name='remover_categoria'),
    path('pedidos_pendentes/', marcar_como_entregue, name='pedidos_pendentes'),
    path('promocoes/', gerenciar_promocoes, name='gerenciar_promocoes'),
    path('remover_promocao/<int:promocao_id>/', remover_promocao, name='remover_promocao'),
    path('subperfil_list/', subperfil_list, name='subperfil_list'),
    path('select_subperfil/<int:subperfil_id>/', select_subperfil, name='select_subperfil'),
    path('edit_subperfil/<int:subperfil_id>/', edit_subperfil, name='edit_subperfil'),
    path('remove_subperfil/<int:subperfil_id>/', remove_subperfil, name='remove_subperfil'),
    path('update_foto/', update_foto, name='update_foto'),
    path('distribuir_pontos/', distribuir_pontos, name='distribuir_pontos'),
    path('aceitar_convite/<int:lojafunc_id>/', aceitar_convite, name='aceitar_convite'),
    path('password_reset/',auth_views.PasswordResetView.as_view(form_class=EmailPasswordResetForm, html_email_template_name='registration/password_reset_email.html',), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),  
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/reset_done.html'), name='password_reset_complete'),
    



]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)