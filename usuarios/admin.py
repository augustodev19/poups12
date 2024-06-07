from django.contrib import admin
from .models import *




class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome',  'email')
    search_fields = ('nome', 'email')


class LojaAdmin(admin.ModelAdmin):
    list_display = ('nomeLoja',  'email')
    search_fields = ('nomeLoja', 'email')






admin.site.register(Cliente, ClienteAdmin)

admin.site.register(CategoriaProduto)
admin.site.register(Produto)
admin.site.register(Promocao)
admin.site.register(CompraAcumulada)
admin.site.register(Categoria)
admin.site.register(Endereco)
admin.site.register(Pedido)
admin.site.register(Charge)
admin.site.register(Subperfil)
admin.site.register(LojaFuncionario)
admin.site.register(ItemPedido)




admin.site.register(Loja, LojaAdmin)

