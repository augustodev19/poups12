from django.shortcuts import render, get_object_or_404
from usuarios.models import *
from decimal import Decimal
from django.contrib import messages
from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.mail import send_mail
from pagseguro import PagSeguro

from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from .models import *
import mercadopago
from django.urls import reverse


import xml.etree.ElementTree as ET

from django.contrib import messages

from usuarios.models import *
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import urllib.parse

from django.http import HttpResponse, JsonResponse

from shapely.geometry import Point
from shapely.ops import nearest_points
from django.contrib.auth.decorators import login_required
from math import radians, cos, sin, asin, sqrt
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Create your views here.
def home_view(request):
    
    categorias = Categoria.objects.all()
    lojas = Loja.objects.all()
    if request.user.is_authenticated:
        try:
            cliente = request.user.cliente  # Substitua 'cliente' pelo nome correto do campo no seu modelo
        except AttributeError:
            cliente = None
    else:
        cliente = None

    if request.user.is_authenticated:
        try:
            loja = request.user.loja  # Substitua 'cliente' pelo nome correto do campo no seu modelo
        except AttributeError:
            loja = None
    else:
        loja = None

    context = {
        'lojas':lojas,
        'categorias':categorias,
        'cliente': cliente,
        'loja':loja,
    }
    return render(request, 'core/index.html', context)


import math
def haversine(lon1, lat1, lon2, lat2):
    # Raio da Terra em Km
    raio_terra_km = 6371.0

    # Conversão de graus em radianos
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Diferença das coordenadas
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Fórmula de Haversine
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    distancia_km = raio_terra_km * c
    return distancia_km


@csrf_exempt
def set_location(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Agora você está recebendo também o endereço formatado
            address = data['address']
            latitude = data['latitude']
            longitude = data['longitude']
            print(data)
            # Salve essas informações na sessão do usuário
            request.session['user_location'] = {
                'address': address,
                'latitude': latitude,
                'longitude': longitude
            }
        
            return JsonResponse({'success': True, 'message': 'Localização definida com sucesso'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)
def loja(request):
    # Buscar todas as categorias
    categorias = Categoria.objects.all()

    # Definir cliente e localização
    cliente = None
    if request.user.is_authenticated and hasattr(request.user, 'cliente'):
        cliente = request.user.cliente
        latitude = cliente.endereco.latitude if cliente.endereco and cliente.endereco.latitude else None
        longitude = cliente.endereco.longitude if cliente.endereco and cliente.endereco.longitude else None
    else:
        user_location = request.session.get('user_location')
        latitude = user_location.get('latitude') if user_location else None
        longitude = user_location.get('longitude') if user_location else None
        adress = user_location.get('adress') if user_location else None

    # Inicializar todas_lojas
    todas_lojas = Loja.objects.filter(is_active=True)

    # Aplicar filtro de categoria se categoria_id for fornecido
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        todas_lojas = todas_lojas.filter(categorias__id=categoria_id)

    # Aplicar filtro de distância e frete grátis
    raio = int(request.GET.get('distancia', 10))
    frete_gratis = request.GET.get('freteGratis') == 'sim'
    lojas_proximas = []

    if latitude is not None and longitude is not None:
        localizacao_usuario = (longitude, latitude)

        for loja in todas_lojas:
            if loja.endereco and loja.endereco.latitude and loja.endereco.longitude:
                distancia = haversine(localizacao_usuario[0], localizacao_usuario[1], loja.endereco.longitude, loja.endereco.latitude)
                if distancia <= raio:
                    if not frete_gratis or loja.valor_frete == 0:
                        loja.distancia_calculada = distancia
                        lojas_proximas.append(loja)
    if not lojas_proximas:
        mensagem_nenhuma_loja = "Nenhuma loja encontrada dentro do raio especificado."
    else:
        mensagem_nenhuma_loja = None                    

    if request.user.is_authenticated:
        try:
            cliente = request.user.cliente  # Substitua 'cliente' pelo nome correto do campo no seu modelo
        except AttributeError:
            cliente = None
    else:
        cliente = None

    if request.user.is_authenticated:
        try:
            loja = request.user.loja  # Substitua 'cliente' pelo nome correto do campo no seu modelo
        except AttributeError:
            loja = None
    else:
        loja = None
                        
    user_location = request.session.get('user_location', {})  # Usa um dict vazio como padrão

    # Preparar o contexto para o template
    context = {
        'user_location':user_location,
        'loja':loja,
        'cliente':cliente,
        'lojas': lojas_proximas,
        'categorias': categorias,
        'mensagem_nenhuma_loja': mensagem_nenhuma_loja,  # Adicione a mensagem ao contexto
    }

    return render(request, 'core/loja.html', context)


def listar_lojas(request):
    categorias = request.GET.get('categorias')
    if categorias:
        lojas = Loja.objects.filter(categorias__id=categorias)
    else:
        lojas = Loja.objects.all()

    # Passar lojas e categorias para o template
    context = {'lojas': lojas}
    return render(request, 'core/listar_lojas.html', context)


def editar_perfil(request):
    return render(request, 'core/editar_perfil.html')
import mercadopago
from django.shortcuts import redirect



# views.py
import requests
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


MERCADO_PAGO_PUBLIC_KEY = 'APP_USR-c79e3c7a-e8d0-4721-9a5e-2dad44492f75'
MERCADO_PAGO_ACCESS_TOKEN = 'APP_USR-59977399911432-110210-7d39b5cafcec9b58b960954a9d495897-1323304242'

# Configure a SDK do Mercado Pago com sua Access Token
sdk = mercadopago.SDK(MERCADO_PAGO_ACCESS_TOKEN)

def payment(request):
    # Verifique se o usuário está autenticado, se necessário
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')  # Redirecione para a página de login, se necessário

    user = request.user
    if 'amount' not in request.GET:
        return render(request, 'core/pagamento.html')  # Substitua 'nome_do_template.html' pelo seu template

    # Obtenha o valor do depósito da query string
    amount = request.GET.get('amount', 0)

    # Garanta que o valor é um float
    try:
        amount = float(amount)
    except ValueError:
        # Trate o caso em que o valor não é um número válido
        return render(request, 'core/pagamento.html', {'error': 'Valor inválido'})


    # Crie a preferência de pagamento
    preference_data = {
        "items": [
            {
                "title": "Depósito de Saldo",
                "quantity": 1,
                "unit_price": float(amount),
            }
        ],
        "payer": {
            "email": user.email,  # Assumindo que o usuário tem um campo de e-mail
        },
        # Adicione outras configurações conforme necessário
    }

    preference_response = sdk.preference().create(preference_data)
    preference_id = preference_response["response"]["id"]

    # Redirecionar o usuário para a página de pagamento do Mercado Pago
    return HttpResponseRedirect(f"https://www.mercadopago.com.br/checkout/v1/redirect?pref_id={preference_id}")


@csrf_exempt
def payment_notification(request):
    if request.method == 'POST':
        # Processar a requisição. Aqui, você extrairá os dados necessários da requisição.
        # O formato exato dependerá de como o Mercado Pago envia esses dados.
        # Vamos assumir que os dados chegam em formato JSON.

        data = json.loads(request.body)
        payment_id = data.get('data', {}).get('id')
        payment_status = data.get('status')

        if payment_status == 'approved':
            # Supondo que você armazene o e-mail do cliente em cada transação
            cliente_email = data.get('payer', {}).get('email')
            amount = data.get('transaction_amount')

            try:
                cliente = Cliente.objects.get(email=cliente_email)
                cliente.saldo_moeda_virtual += Decimal(amount)
                cliente.save()
            except Cliente.DoesNotExist:
                # Lidar com a situação em que o cliente não é encontrado
                pass

        return JsonResponse({'status': 'ok'})

    return JsonResponse({'error': 'invalid request'}, status=400)


stripe.api_key = 'sk_test_51OUOvLK0evm2fcdGJpwO9LInadGfiwH2U0ftWu4DIQo32A6c5bTeUYwiKmvdSsdL3GhZyjw9p3d75sqzTKHQF0VR001NrAgjhZ'

def comprar_credito(request):
    if request.method == 'POST':
        valor_credito = int(request.POST.get('valor_credito'))  # valor em Reais

        # Verificar se request.user é uma instância de Cliente
        try:
            # Supondo que Cliente tenha uma relação um-para-um com User
            cliente = request.user.cliente
        except Cliente.DoesNotExist:
            # Tratar caso em que o perfil de cliente não existe
            return redirect('login')  # Redirecionar para um local apropriado

        # Atualizar o saldo do cliente antecipadamente
        cliente.saldo_poups += Decimal(valor_credito)
        cliente.save()

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'brl',
                    'unit_amount': valor_credito * 100,  # Convertendo para centavos
                    'product_data': {
                        'name': 'Crédito para conta',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/credito_sucesso/'),
            cancel_url=request.build_absolute_uri('/credito_cancelado/'),
        )

        return redirect(checkout_session.url, code=303)

    # Certifique-se de que esta linha está alinhada corretamente com o "if" acima
    return render(request, 'core/comprar_credito.html')


def loja1(request):
    lojas = Loja.objects.all()
    context = {
        'lojas':lojas
    }
    return render(request, 'core/loja1.html', context)



def add_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            # Aqui você pode associar a categoria à loja, se necessário
            return redirect('alguma-url')
    else:
        form = CategoriaForm()
    return render(request, 'add_categoria.html', {'form': form})

def edit_categoria(request, categoria_id):
    categoria = Categoria.objects.get(id=categoria_id)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('alguma-url')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'edit_categoria.html', {'form': form, 'categoria': categoria})


def credito_sucesso(request):
    messages.success(request, f'Compra realizada com sucesso!')
    return redirect('home')



def perfil_loja(request, loja_id):
    loja = get_object_or_404(Loja, id=loja_id)
    if request.user.cliente:
        cliente = request.user.cliente
    else:
        cliente = None

    
    context = {
        'perfil_loja':loja,
        'cliente':cliente
    }

    return render(request, 'core/perfil_loja.html', context)


def detalhes_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    loja = produto.categoria.loja if produto.categoria else None

    context = {'produto': produto,
    'loja': loja}
    return render(request, 'core/detalhes_produto.html', context )

from django.shortcuts import get_object_or_404, redirect


from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
import json

@require_http_methods(["POST"])
def adicionar_ao_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    loja_id = produto.categoria.loja.id if produto.categoria.loja else None

    if not loja_id:
        return JsonResponse({'erro': 'Produto sem loja associada'}, status=400)

    if 'carrinho' not in request.session:
        request.session['carrinho'] = {'loja_id': loja_id, 'itens': {}}

    carrinho = request.session['carrinho']

    if carrinho['loja_id'] != loja_id:
        carrinho['itens'] = {}
        carrinho['loja_id'] = loja_id

    item_key = str(produto_id)
    if item_key in carrinho['itens']:
        carrinho['itens'][item_key]['quantidade'] += 1
    else:
        carrinho['itens'][item_key] = {
            'produto_id': produto_id,
            'quantidade': 1,
            'preco': str(produto.preco),
            'pontos': str(produto.pontos),
            'nome': produto.nome,
            'imagem_url': produto.foto.url if produto.foto else None  # Salvando a URL da imagem

        }

    request.session.modified = True
    return JsonResponse({
        'carrinho': carrinho,
        'sucesso': True,
        'mensagem': 'Adicionado ao Carrinho'
    })

def ver_carrinho(request):
    carrinho = request.session.get('carrinho', {'itens': {}})
    total_geral_carrinho = Decimal('0.00')
    total_pontos_carrinho = 0


    for produto_id, produto_info in carrinho.get('itens', {}).items():
        produto = get_object_or_404(Produto, id=produto_id)
        produto_info['imagem_url'] = produto.foto.url if produto.foto else None

        preco = Decimal(produto_info['preco'])
        quantidade = int(produto_info['quantidade'])
        pontos = int(produto_info['pontos'])

        total_geral_carrinho += preco * quantidade
        total_pontos_carrinho += pontos * quantidade

    return render(request, 'core/carrinho.html', {
        'carrinho': carrinho,
        'total_geral_carrinho': total_geral_carrinho,
        'total_pontos_carrinho': total_pontos_carrinho
    })

def remover_do_carrinho(request, produto_id):
    carrinho = request.session.get('carrinho', {'itens': {}})
    if str(produto_id) in carrinho['itens']:
        del carrinho['itens'][str(produto_id)]
        request.session.modified = True
        return JsonResponse({'status': 'success', 'message': 'Item removido com sucesso.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Item não encontrado no carrinho.'})


def checkout(request):
    carrinho = request.session.get('carrinho', {'itens': {}})
    cliente = request.user.cliente if request.user.is_authenticated and hasattr(request.user, 'cliente') else None
    endereco = cliente.endereco if cliente else None
    total_geral_carrinho = Decimal('0.00')

    # Aqui, vamos garantir que a imagem_url está sendo passada corretamente
    itens_completos = []
    for produto_id, item in carrinho.get('itens', {}).items():
        produto = get_object_or_404(Produto, id=produto_id)
        item['imagem_url'] = produto.foto.url if produto.foto else None
        item['nome'] = produto.nome  # Já deve estar definido, mas só para garantir
        preco = Decimal(item['preco'])
        quantidade = item['quantidade']
        total_geral_carrinho += preco * quantidade
        itens_completos.append(item)  # Adiciona o item atualizado à lista

    return render(request, 'core/checkout.html', {
        'itens': itens_completos,  # Passa os itens atualizados para o template
        'cliente': cliente,
        'endereco': endereco,
        'total_geral': total_geral_carrinho
    })
from urllib.parse import urlencode
def log_response(response):
    """Log detalhado da resposta da API."""
    logger.error(f"Status Code: {response.status_code}")
    logger.error(f"Headers: {response.headers}")
    try:
        logger.error(f"Body: {response.json()}")
    except ValueError:
        # Para respostas que não são JSON, logue o corpo da resposta como está
        logger.error(f"Raw Body: {response.text}")
# Configure o logger
logger = logging.getLogger(__name__)
# Configure o logger para registrar informações sobre a requisição
logger = logging.getLogger(__name__)


@csrf_exempt
def pagamento_notificacao(request):
    # Lógica para lidar com a notificação de pagamento do Mercado Pago
    # Aqui você pode atualizar o status do pedido no seu banco de dados, enviar e-mails de confirmação, etc.
    # Certifique-se de validar a autenticidade da notificação para evitar fraudes.
    return HttpResponse(status=200)

def pagamento_sucesso(request):
    # View para lidar com o redirecionamento de sucesso do pagamento
    return HttpResponse("Pagamento bem-sucedido! Obrigado por sua compra.")

def pagamento_falha(request):
    # View para lidar com o redirecionamento de falha do pagamento
    return HttpResponse("O pagamento falhou. Por favor, tente novamente.")

def pagamento_pendente(request):
    # View para lidar com o redirecionamento de pagamento pendente
    return HttpResponse("Seu pagamento está pendente de confirmação. Aguarde a confirmação.")

from urllib.parse import urljoin
from django.http import JsonResponse, HttpResponseRedirect


def get_pagseguro_api():
    pg = PagSeguro(email="augusto.webdeveloping@gmail.com", token="39FD640937A14E0A91310DEDE47AFF72", config={'sandbox': True})
    return pg

@login_required
def criar_pagamento_checkout(request):
    pg = get_pagseguro_api()
    carrinho = request.session.get('carrinho', {'itens': {}})

    if not carrinho['itens']:
        return JsonResponse({"erro": "Carrinho vazio."}, status=400)

    items = []
    total_geral_carrinho = 0

    for item_id, item in carrinho['itens'].items():
        produto = Produto.objects.get(id=item_id)
        pg.add_item(
            id=str(produto.id),
            description=produto.nome,
            amount=format(produto.preco, '.2f'),
            quantity=item['quantidade']
        )
        total_geral_carrinho += produto.preco * int(item['quantidade'])

    response = pg.checkout()
    preference_id = response.code  # O código de referência do PagSeguro

    request.session['preference_id'] = preference_id  # Armazenando o ID da preferência na sessão
    return redirect(response.payment_url)  # Redirecionar para a página de pagamento do PagSeguro
    
def enviar_email_pedido(request, pedido, itens_pedido):
    try:
        pedido_url = request.build_absolute_uri(reverse('pedido_detalhe', args=[pedido.id]))  # 'pedido_detalhe' é o nome da URL para visualizar o pedido
        subject = 'Detalhes do Seu Pedido'
        message = f"Olá {pedido.cliente.nome},\n\nSeu pedido foi criado com sucesso!\n\nDetalhes do Pedido:\n"
        for item in itens_pedido:
            message += f"- {item.produto.nome} (Quantidade: {item.quantidade}, Preço: R${item.preco_unitario})\n"
        message += f"\nTotal do Pedido: R${pedido.total}\n"
        message += f"Você pode visualizar seu pedido aqui: {pedido_url}\n\nObrigado por comprar conosco!"
        
        send_mail(subject, message, 'seuemail@dominio.com', [pedido.cliente.email])
        messages.success(request, "Email com detalhes do pedido enviado com sucesso.")
    except Exception as e:
        messages.error(request, f"Erro ao enviar email: {str(e)}")
@require_http_methods(["POST"])
def confirmar_pagamento(request):
    notification_code = request.POST.get('notificationCode', None)
    if notification_code:
        pg = get_pagseguro_api()
        transaction = pg.check_notification(notification_code)
        
        if transaction.status == '3':  # Código '3' indica que o pagamento foi confirmado
            # Recupera os detalhes do carrinho armazenados na sessão
            carrinho = request.session.get('carrinho', {'itens': {}})
            cliente_id = request.session.get('cliente_id')
            loja_id = request.session.get('loja_id')
            endereco = request.session.get('endereco')

            if not carrinho['itens']:
                messages.error(request, 'Carrinho vazio.')
                return redirect('home')

            cliente = Cliente.objects.get(id=cliente_id)
            loja = Loja.objects.get(id=loja_id)

            # Cria o pedido
            pedido = Pedido.objects.create(
                cliente=cliente,
                loja=loja,
                total=request.session.get('total_geral_carrinho'),
                pontos=request.session.get('total_pontos_carrinho'),
                confirmado=True,
                localizacao=endereco
            )

            # Cria os itens do pedido
            for item_id, item in carrinho['itens'].items():
                produto = Produto.objects.get(id=item_id)
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=produto,
                    quantidade=item['quantidade'],
                    preco_unitario=item['preco'],
                    imagem_url=item.get('imagem_url', None)
                )

            # Enviando o email com os detalhes do pedido
            enviar_email_pedido(request, pedido, pedido.itempedido_set.all())

            # Limpar a sessão após criar o pedido
            keys_to_delete = ['carrinho', 'total_geral_carrinho', 'total_pontos_carrinho', 'endereco', 'loja_id', 'cliente_id', 'preference_id']
            for key in keys_to_delete:
                if key in request.session:
                    del request.session[key]

            messages.success(request, 'Pedido criado e confirmado com sucesso!')
            return redirect('home')
        else:
            messages.error(request, 'Pagamento não confirmado.')
            return redirect('home')
    else:
        messages.error(request, 'Notificação inválida.')
        return redirect('home')