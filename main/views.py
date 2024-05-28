from django.shortcuts import render, get_object_or_404
from usuarios.models import *
from decimal import Decimal
from django.contrib import messages
from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
import secrets  # Importe esta biblioteca no início do arquivo
import os
import hashlib
from django.core.cache import cache
from poupsapp.tasks import *
import hmac
from django.views import View
from mercadopago import SDK

from email.mime.image import MIMEImage

from django.urls import reverse

from pagseguro import PagSeguro
import qrcode
import base64
from urllib.parse import quote_plus
from django.template.loader import render_to_string
from bs4 import BeautifulSoup
from django.core.mail import EmailMultiAlternatives
from decimal import Decimal
from django.http import HttpResponse
from io import BytesIO
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


def teste_tarefa(request):
    pedido_id_novo = 291  # ID do pedido para teste
    charge_id = 2
    check_charge_status.apply_async((charge_id,), countdown=3)
    #recusar_pedido_automaticamente.apply_async((pedido_id_novo,), countdown=10)  # Atraso de 10 minutos
    return JsonResponse({'status': 'Pix checkado'})


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

def add_view(request):
    result = add.delay(4, 6)
    return JsonResponse({'task_id': result.id})

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


stripe.api_key = 'sk_test_51PHMq7CFqCCeinfhM7MDQ086AzXSszH5S6SbmHzNo2GnysN3AfZvJeVYzD8myLBvTHdCWqFQRfxTfFciwf2DFc3m00k6zHcMzu'
@login_required
def comprar_credito(request):
    if request.method == 'POST':
        valor_credito = Decimal(request.POST.get('valor_credito'))

        # Calculando pontos
        pontos_a_adicionar = valor_credito / Decimal('0.4')

        # Configuração do SDK do Stripe
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'brl',
                        'product_data': {
                            'name': 'Compra de pontos',
                        },
                        'unit_amount': int(valor_credito * 100),  # Converte para centavos
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(reverse('editar_cliente')),
                cancel_url=request.build_absolute_uri('/credito_cancelado/'),
                metadata={
                    'user_id': request.user.id,
                    'pontos_a_adicionar': str(pontos_a_adicionar),
                    'is_credit_purchase': 'true'  # Flag para indicar compra de crédito
                }
            )

            request.session['stripe_session_id'] = session.id  # Guardando o ID da sessão para uso futuro
            return redirect(session.url)

        except Exception as e:
            print("Erro ao criar sessão de checkout:", str(e))
            messages.error(request, "Houve um erro ao criar a sessão de pagamento. Por favor, tente novamente.")
            return redirect('confirmar_compra_credito')

    return render(request, 'core/comprar_credito.html')


@login_required
def confirmar_compra_credito(request):
    if 'pontos_a_adicionar' in request.session:
        pontos_a_adicionar = Decimal(request.session.pop('pontos_a_adicionar'))
        cliente = request.user.cliente
        
        # Adicionar pontos ao cliente
        cliente.pontos += pontos_a_adicionar
        cliente.save()
        
        messages.success(request, "Créditos convertidos em pontos com sucesso!")
    else:
        messages.error(request, "Erro ao converter créditos em pontos.")
    
    return redirect('home')  # Ou redirecione para a página de status do crédito


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
        return redirect('login')

    
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

def detalhes_promocao(request, promocao_id):
    promocao = get_object_or_404(Promocao, id=promocao_id)
    print("Promoção:", promocao)

    try:
        cliente = request.user.cliente
    except Cliente.DoesNotExist:
        messages.error(request, 'Cliente não encontrado.')
        return redirect('home')

    # Corrigindo a obtenção de itens comprados
    compra_acumulada = CompraAcumulada.objects.filter(cliente=cliente, promocao=promocao).first()
    print("Compra Acumulada:", compra_acumulada)
    itens_comprados = compra_acumulada.quantidade_comprada if compra_acumulada else 0
    print("Itens Comprados:", itens_comprados)

    try:
        loja = promocao.loja
    except Loja.DoesNotExist:
        messages.error(request, 'Loja não encontrada.')
        return redirect('home')

    context = {
        'promocao': promocao,
        'loja': loja,
        'cliente': cliente,
        'itens_comprados': itens_comprados
    }
    return render(request, 'core/produtos_promocoes.html', context)


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
        request.session['carrinho'] = {'loja_id': loja_id, 'itens': {}, 'pontos_para_proxima_promocao': {}}

    carrinho = request.session['carrinho']

    if carrinho['loja_id'] != loja_id:
        carrinho['itens'] = {}
        carrinho['pontos_para_proxima_promocao'] = {}
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
            'imagem_url': produto.foto.url if produto.foto else None,
            'promocao': False
        }

    # Verificar se o produto tem promoção
    if produto.promocao and produto.promocao.ativo:
        promocao = produto.promocao
        compra_acumulada, created = CompraAcumulada.objects.get_or_create(
            cliente=request.user.cliente,
            produto=produto,
            promocao=promocao
        )
        
        if item_key not in carrinho['pontos_para_proxima_promocao']:
            carrinho['pontos_para_proxima_promocao'][item_key] = compra_acumulada.pontos_para_proxima_promocao

        # Atualiza a quantidade comprada acumulada e os pontos para a próxima promoção
        compra_acumulada.quantidade_comprada += 1
        carrinho['pontos_para_proxima_promocao'][item_key] += 1
        pontos_acumulados = carrinho['pontos_para_proxima_promocao'][item_key]
        num_promocoes = pontos_acumulados // promocao.quantidade_necessaria

        # Atualiza o carrinho com a quantidade de itens promocionais
        promocao_key = f'promocao_{promocao.id}'
        if promocao_key not in carrinho['itens']:
            carrinho['itens'][promocao_key] = {
                'produto_id': produto_id,
                'quantidade': 0,
                'nome': f"Promoção: {produto.nome}",
                'imagem_url': promocao.imagem.url if promocao.imagem else None,
                'promocao': True,
                'preco': '0.00'
            }
        carrinho['itens'][promocao_key]['quantidade'] = num_promocoes

        # Atualiza a compra acumulada no banco de dados
        compra_acumulada.pontos_para_proxima_promocao = carrinho['pontos_para_proxima_promocao'][item_key] % promocao.quantidade_necessaria
        compra_acumulada.save()

    request.session.modified = True
    return JsonResponse({
        'carrinho': carrinho,
        'sucesso': True,
        'mensagem': 'Adicionado ao Carrinho'
    })
@require_http_methods(["POST"])
def remover_do_carrinho(request, produto_id):
    carrinho = request.session.get('carrinho', {'itens': {}, 'pontos_para_proxima_promocao': {}})
    produto_id_str = str(produto_id)

    if produto_id_str in carrinho['itens']:
        produto = get_object_or_404(Produto, id=produto_id)
        quantidade_removida = carrinho['itens'][produto_id_str]['quantidade']
        
        # Verificar se o produto tem promoção
        if produto.promocao and produto.promocao.ativo:
            promocao = produto.promocao
            compra_acumulada = CompraAcumulada.objects.get(
                cliente=request.user.cliente,
                produto=produto,
                promocao=promocao
            )
            
            item_key = produto_id_str
            if item_key in carrinho['pontos_para_proxima_promocao']:
                carrinho['pontos_para_proxima_promocao'][item_key] -= quantidade_removida
                if carrinho['pontos_para_proxima_promocao'][item_key] < 0:
                    carrinho['pontos_para_proxima_promocao'][item_key] = 0

                # Remover itens promocionais se não houver quantidade suficiente
                promocao_key = f'promocao_{promocao.id}'
                quantidade_promocional = carrinho['itens'].get(promocao_key, {}).get('quantidade', 0)
                while quantidade_promocional > 0 and carrinho['pontos_para_proxima_promocao'][item_key] < promocao.quantidade_necessaria:
                    carrinho['itens'][promocao_key]['quantidade'] -= 1
                    quantidade_promocional -= 1
                    if carrinho['itens'][promocao_key]['quantidade'] == 0:
                        del carrinho['itens'][promocao_key]

                # Atualiza a compra acumulada no banco de dados
                compra_acumulada.quantidade_comprada -= quantidade_removida
                if compra_acumulada.quantidade_comprada < 0:
                    compra_acumulada.quantidade_comprada = 0

                compra_acumulada.pontos_para_proxima_promocao = carrinho['pontos_para_proxima_promocao'][item_key] % promocao.quantidade_necessaria
                compra_acumulada.save()

        del carrinho['itens'][produto_id_str]
        request.session.modified = True
        return JsonResponse({'status': 'success', 'message': 'Item removido com sucesso.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Item não encontrado no carrinho.'})
def ver_carrinho(request):
    carrinho = request.session.get('carrinho', {'itens': {}, 'pontos_para_proxima_promocao': {}})
    total_geral_carrinho = Decimal('0.00')
    total_pontos_carrinho = Decimal('0.00')

    itens_normais = []
    itens_promocionais = []

    for item_key, produto_info in carrinho.get('itens', {}).items():
        produto = get_object_or_404(Produto, id=produto_info['produto_id'])
        produto_info['imagem_url'] = produto.foto.url if produto.foto else None

        preco = Decimal(produto_info['preco'])
        quantidade = int(produto_info['quantidade'])
        pontos = Decimal(produto_info.get('pontos', '0.00'))

        if produto_info['promocao']:
            if quantidade > 0:
                produto_info['preco'] = '0.00'
                itens_promocionais.append(produto_info)
        else:
            total_geral_carrinho += preco * quantidade
            total_pontos_carrinho += pontos * quantidade
            itens_normais.append(produto_info)

    return render(request, 'core/carrinho.html', {
        'itens_normais': itens_normais,
        'itens_promocionais': itens_promocionais,
        'total_geral_carrinho': total_geral_carrinho,
        'total_pontos_carrinho': total_pontos_carrinho,
        'pontos_para_proxima_promocao': carrinho.get('pontos_para_proxima_promocao', {})
    })

def checkout1(request):
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
    session_id = request.session.get('stripe_session_id')
    if session_id:
        session = stripe.checkout.Session.retrieve(session_id)
        metadata = session.metadata
        frete = metadata.get('frete', '0.00')
        
        pedido_id = cache.get(f'pedido_id_{session_id}')
        if pedido_id:
            # Limpeza da sessão
            keys_to_delete = [
                'preference_id', 'total_geral_carrinho', 'total_pontos_carrinho',
                'carrinho', 'endereco', 'loja_id', 'cliente_id', 'stripe_session_id'
            ]
            for key in keys_to_delete:
                if key in request.session:
                    del request.session[key]
            
            messages.success(request, 'Pedido criado com sucesso!')
            return redirect('pedido_pagamento', pedido_id=pedido_id)
        else:
            messages.error(request, "Não foi possível encontrar o pedido.")
            return redirect('home')
    else:
        messages.error(request, "Sessão de pagamento não encontrada.")
        return redirect('home')
def pagamento_falha(request):
    # View para lidar com o redirecionamento de falha do pagamento
    messages.error(request, 'O pagamento falhou. Por favor, tente novamente.')
    return redirect('checkout')

def pagamento_pendente(request):
    # View para lidar com o redirecionamento de pagamento pendente
    return HttpResponse("Seu pagamento está pendente de confirmação. Aguarde a confirmação.")

from urllib.parse import urljoin
from django.http import JsonResponse, HttpResponseRedirect


def get_pagseguro_api():
    pg = PagSeguro(email="augusto.webdeveloping@gmail.com", token="39FD640937A14E0A91310DEDE47AFF72", config={'sandbox': True})
    return pg


# Configurações iniciais
ACCESS_TOKEN = 'APP_USR-59977399911432-110210-7d39b5cafcec9b58b960954a9d495897-1323304242'
sdk = SDK(ACCESS_TOKEN)

import json
logger = logging.getLogger(__name__)  # Configuração do logger para a view


API_URL = "https://api.openpix.com.br/api/v1/charge"
HEADERS = {'Authorization': "Q2xpZW50X0lkX2NjNjFiMmI0LWE1N2QtNGE1My05NmVkLWZmOWYyZTFjYjQ0NzpDbGllbnRfU2VjcmV0X1h5b2NuR3hPN0VrRk41aHpzdjg0bTE3ajNHbUpqeWNrbXdoejhBbFUzTTA9"}



def criar_pagamento_pix(request):
    try:
        carrinho = request.session.get('carrinho', {'itens': {}})
        if not carrinho['itens']:
            return JsonResponse({"erro": "Carrinho vazio."}, status=400)

        total_geral_carrinho = Decimal('0.00')
        loja = None

        for item_key, item in carrinho['itens'].items():
            if item_key.startswith('promocao_'):
                continue  # Ignore promotional items in this loop

            produto = get_object_or_404(Produto, id=item['produto_id'])
            if not loja:
                loja = produto.categoria.loja

            quantidade = int(item['quantidade'])
            total_geral_carrinho += Decimal(item['preco']) * quantidade

        if loja is None:
            return JsonResponse({"erro": "Informações da loja não disponíveis."}, status=400)

        valor_frete = Decimal(loja.valor_frete)
        total_geral_carrinho += valor_frete

        endereco = request.POST.get('endereco')
        request.session['total_geral_carrinho'] = str(total_geral_carrinho)
        request.session['endereco'] = endereco
        request.session['loja_id'] = loja.id
        request.session['cliente_id'] = request.user.cliente.id

        correlation_id = str(uuid.uuid4())
        data = {
            "value": int(total_geral_carrinho * 100),  # Valor em centavos
            "correlationID": correlation_id,
            "comment": "Pagamento via Pix",
            "customer": {},
        }

        response = requests.post(API_URL, headers=HEADERS, json=data)
        print(f"Resposta da API ao criar cobrança: {response.status_code}, {response.text}")
        charge_data = response.json()

        if 'charge' not in charge_data or 'identifier' not in charge_data['charge']:
            raise ValueError("Erro ao criar a cobrança: resposta inesperada da API")

        charge = Charge.objects.create(
            charge_id=charge_data['charge']['identifier'],
            correlation_id=correlation_id,
            status=charge_data['charge']['status'],
            total=total_geral_carrinho,
            endereco=endereco,
            loja_id=loja.id,
            cliente_id=request.user.cliente.id,
            attempts=0,  # Iniciar o número de tentativas em 0
            last_error=None  # Iniciar sem erros
        )

        request.session['pix_charge_id'] = charge.charge_id

        # Agendar a tarefa para verificar o status da cobrança
        check_charge_status.apply_async((correlation_id, timezone.now().isoformat()), countdown=3)
        print(f"Tarefa agendada para verificar o status da cobrança com correlation_id {correlation_id} em 3 segundos")

        # Renderizar a página HTML com o QR Code e status de verificação
        return render(request, 'core/charge_detail.html', {
            'charge_data': charge_data['charge'],
            'attempts': charge.attempts,
            'last_error': charge.last_error
        })

    except Exception as e:
        messages.error(request, f"Erro ao criar pagamento Pix: {str(e)}")
        return redirect('checkout')
API_URL = "https://api.openpix.com.br/api/v1/charge"
HEADERS = {'Authorization': "Q2xpZW50X0lkX2NjNjFiMmI0LWE1N2QtNGE1My05NmVkLWZmOWYyZTFjYjQ0NzpDbGllbnRfU2VjcmV0X1h5b2NuR3hPN0VrRk41aHpzdjg0bTE3ajNHbUpqeWNrbXdoejhBbFUzTTA9"}

def handle_pix_payment(charge_id):
    try:
        charge = Charge.objects.get(charge_id=charge_id)
        if charge.status == 'paid':
            total_geral_carrinho = Decimal(charge.total)
            endereco = charge.endereco
            loja_id = charge.loja_id
            cliente_id = charge.cliente_id

            cliente = Cliente.objects.get(id=cliente_id)
            loja = Loja.objects.get(id=loja_id)

            pedido = Pedido.objects.create(
                cliente=cliente,
                loja=loja,
                total=total_geral_carrinho,
                pontos=total_geral_carrinho * 0.4,
                status='pendente',
                pagamento='pix',
                localizacao=endereco,
                payment_id=charge_id
            )

            carrinho = cache.get(f'carrinho_{charge.cliente_id}', {'itens': {}, 'pontos_para_proxima_promocao': {}})
            for item_key, item in carrinho['itens'].items():
                if item_key.startswith('promocao_'):
                    continue  # Ignore promotional items in this loop

                produto = Produto.objects.get(id=item['produto_id'])
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=produto,
                    quantidade=item['quantidade'],
                    preco_unitario=Decimal(item['preco'])
                )

            enviar_email_pedido(None, pedido, pedido.itempedido_set.all())
            cache.set(f"pedido_id_{charge_id}", pedido.id, timeout=300)
            print(f"Pedido ID salvo no cache: {cache.get(f'pedido_id_{charge_id}')}")

    except Cliente.DoesNotExist:
        print(f"Cliente ID {cliente_id} não encontrado.")
    except Loja.DoesNotExist:
        print(f"Loja ID {loja_id} não encontrada.")
    except Produto.DoesNotExist:
        print(f"Produto não encontrado.")
    except Exception as e:
        print(f"Erro ao processar o pagamento Pix: {str(e)}")


@login_required
@require_http_methods(["POST"])
def criar_pagamento_checkout(request):
    try:
        carrinho = request.session.get('carrinho', {'itens': {}})
        if not carrinho['itens']:
            return JsonResponse({"erro": "Carrinho vazio."}, status=400)

        items = []
        total_geral_carrinho = Decimal('0.00')
        total_pontos_carrinho = 0
        loja = None

        for item_key, item in carrinho['itens'].items():
            produto = get_object_or_404(Produto, id=item['produto_id'])
            if not loja:
                loja = produto.categoria.loja

            quantidade = int(item['quantidade'])
            if quantidade < 1:
                continue

            unit_amount = 0 if item['promocao'] else int(Decimal(item['preco']) * 100)
            items.append({
                'price_data': {
                    'currency': 'brl',
                    'product_data': {
                        'name': item['nome'],
                    },
                    'unit_amount': unit_amount,
                },
                'quantity': quantidade,
            })

            if not item['promocao']:
                total_geral_carrinho += Decimal(item['preco']) * quantidade
            total_pontos_carrinho += produto.pontos * quantidade

        if loja is None:
            return JsonResponse({"erro": "Informações da loja não disponíveis."}, status=400)

        valor_frete = Decimal(loja.valor_frete)
        total_geral_carrinho += valor_frete

        items.append({
            'price_data': {
                'currency': 'brl',
                'product_data': {
                    'name': 'Frete',
                },
                'unit_amount': int(valor_frete * 100),
            },
            'quantity': 1,
        })

        endereco = request.POST.get('endereco')
        request.session['total_geral_carrinho'] = str(total_geral_carrinho)
        request.session['total_pontos_carrinho'] = total_pontos_carrinho
        request.session['endereco'] = endereco
        request.session['loja_id'] = loja.id
        request.session['cliente_id'] = request.user.cliente.id

        subperfil_id = request.session.get('subperfil_id')
        subperfil_nome = None
        if subperfil_id:
            subperfil = get_object_or_404(Subperfil, id=subperfil_id)
            subperfil_nome = subperfil.nome

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=items,
            mode='payment',
            success_url=request.build_absolute_uri(reverse('pagamento_sucesso')),
            cancel_url=request.build_absolute_uri(reverse('pagamento_falha')),
            metadata={
                'user_id': request.user.id,
                'loja_id': loja.id,
                'total_geral_carrinho': str(total_geral_carrinho),
                'total_pontos_carrinho': total_pontos_carrinho,
                'endereco': endereco,
                'frete': str(valor_frete),
                'subperfil_nome': subperfil_nome
            }
        )
        request.session['stripe_session_id'] = session.id
        return redirect(session.url)
    except Exception as e:
        messages.error(request, f"Erro ao criar pagamento: {str(e)}")
        return redirect('checkout')
@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            print(f"Invalid payload: {e}")
            return JsonResponse({'status': 'invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError as e:
            print(f"Invalid signature: {e}")
            return JsonResponse({'status': 'invalid signature'}, status=400)

        print(f"Event received: {event['type']}")

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            if session['payment_status'] == 'paid':
                handle_checkout_session(request, session)
        elif event['type'] == 'charge.refunded':
            charge = event['data']['object']
            payment_intent_id = charge['payment_intent']
            handle_refund(payment_intent_id)
        elif event['type'] == 'payout.paid':
            payout = event['data']['object']
            handle_payout(payout)

        return JsonResponse({'status': 'success'}, status=200)

def handle_checkout_session(request, session):
    metadata = session.get('metadata', {})
    user_id = metadata.get('user_id')
    subperfil_nome = metadata.get('subperfil_nome', None)
    is_credit_purchase = metadata.get('is_credit_purchase', 'false') == 'true'

    print(f"Handling checkout session for user: {user_id}")

    if is_credit_purchase:
        pontos_a_adicionar = Decimal(metadata.get('pontos_a_adicionar', '0'))
        handle_credit_purchase(user_id, pontos_a_adicionar)
    else:
        handle_order_purchase(session, metadata, user_id, subperfil_nome)

    # Limpar a sessão após o pagamento bem-sucedido
    request.session['carrinho'] = {}
    request.session['stripe_session_id'] = None
    request.session.modified = True
def handle_credit_purchase(user_id, pontos_a_adicionar):
    try:
        cliente = Cliente.objects.get(id=user_id)
        cliente.pontos += pontos_a_adicionar
        cliente.save()
        print(f"Créditos adicionados para o cliente {cliente.id}.")
    except Cliente.DoesNotExist:
        print(f"Cliente ID {user_id} não encontrado.")
    except Exception as e:
        print(f"Erro ao processar a sessão do checkout: {str(e)}")

def handle_order_purchase(session, metadata, user_id, subperfil_nome):
    loja_id = metadata.get('loja_id')
    total_geral_carrinho = float(metadata.get('total_geral_carrinho', 0))
    total_pontos_carrinho = int(metadata.get('total_pontos_carrinho', 0))
    endereco = metadata.get('endereco', '')

    print(f"Processing order for user: {user_id}")

    try:
        cliente = Cliente.objects.get(id=user_id)
        loja = Loja.objects.get(id=loja_id)

        pedido = Pedido.objects.create(
            cliente=cliente,
            loja=loja,
            total=total_geral_carrinho,
            pontos=total_geral_carrinho * 0.4,
            status='pendente',
            pagamento='reais',
            localizacao=endereco,
            payment_id=session['payment_intent']
        )

        print(f"Pedido criado: {pedido.id}")

        line_items = stripe.checkout.Session.list_line_items(session.id)
        carrinho = session.get('carrinho', {'itens': {}, 'pontos_para_proxima_promocao': {}})
        for item in line_items.data:
            if item.description.lower() == "frete":
                print("Item de frete encontrado, pulando...")
                continue

            try:
                produto = Produto.objects.get(nome=item.description)
                preco_unitario = Decimal(item.amount_total) / 100 if not produto.promocao else Decimal('0.00')
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=produto,
                    quantidade=item.quantity,
                    preco_unitario=preco_unitario
                )
                print(f"Item adicionado ao pedido: {produto.nome}, quantidade: {item.quantity}, preço unitário: {preco_unitario}")

                # Atualizar pontos para próxima promoção no banco de dados
                if produto.promocao:
                    compra_acumulada, created = CompraAcumulada.objects.get_or_create(
                        cliente=cliente, produto=produto, promocao=produto.promocao
                    )
                    compra_acumulada.quantidade_comprada += item.quantity
                    if str(produto.id) in carrinho['pontos_para_proxima_promocao']:
                        compra_acumulada.pontos_para_proxima_promocao += carrinho['pontos_para_proxima_promocao'][str(produto.id)]
                    compra_acumulada.save()

            except Produto.DoesNotExist:
                print(f"Produto não encontrado: {item.description}")

        enviar_email_pedido(None, pedido, pedido.itempedido_set.all(), subperfil_nome)

        print("Email de pedido enviado")

        cache.set(f"pedido_id_{session.id}", pedido.id, timeout=300)
        print(f"Pedido ID salvo no cache: {cache.get(f'pedido_id_{session.id}')}")

    except Cliente.DoesNotExist:
        print(f"Cliente ID {user_id} não encontrado.")
    except Loja.DoesNotExist:
        print(f"Loja ID {loja_id} não encontrada.")
    except Produto.DoesNotExist:
        print(f"Produto não encontrado.")
    except Exception as e:
        print(f"Erro ao processar a sessão do checkout: {str(e)}")

    # Limpar a sessão após o pagamento bem-sucedido
    session['carrinho'] = {'itens': {}, 'promocoes': {}, 'pontos_para_proxima_promocao': {}}
    session.modified = True

def handle_payout(payout):
    try:
        loja = Loja.objects.get(stripe_payout_id=payout['id'])
        loja.saldo -= Decimal(payout['amount']) / 100
        loja.save()
        print(f"Payout processado para a loja {loja.id}.")
    except Loja.DoesNotExist:
        print(f"Loja com payout ID {payout['id']} não encontrada.")
    except Exception as e:
        print(f"Erro ao processar o payout: {str(e)}")


def sacar_dinheiro(request):
    loja = request.user.loja
    if request.method == 'POST':
        valor = Decimal(request.POST.get('valor'))
        stripe_token = request.POST.get('stripeToken')

        if valor > loja.saldo:
            messages.error(request, "Você não pode sacar um valor maior que o saldo disponível.")
            return redirect('sacar_dinheiro')

        print(f"Token recebido: {stripe_token}")  # Log temporário

        try:
            # Criando uma transferência para o cartão usando o token
            charge = stripe.Charge.create(
                amount=int(valor * 100),  # Valor em centavos
                currency="brl",
                source=stripe_token,
                description="Saque da loja",
                receipt_email=request.user.email
            )

            if charge.status == 'succeeded':
                # Subtraindo o valor do saldo da loja
                loja.saldo -= valor
                loja.save()  # Salvando as alterações no modelo da loja

                messages.success(request, "Saque realizado com sucesso!")
                return redirect('sacar_dinheiro')
            else:
                messages.error(request, f"Falha ao realizar saque: {charge.failure_message}")
                return redirect('sacar_dinheiro')

        except stripe.error.StripeError as e:
            messages.error(request, f"Falha ao realizar saque: {str(e)}")
            return redirect('sacar_dinheiro')

    context = {
        'loja': loja,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY  # Passa a chave pública Stripe para o template
    }
    return render(request, 'core/financeiro.html', context)

@csrf_exempt
def confirmar_pagamento(request):
    session_id = request.session.get('stripe_session_id')
    if session_id:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == 'paid':
            loja_id = request.session.get('loja_id')
            cliente_id = request.user.id  # Assuming the user ID is the customer ID

            loja = Loja.objects.get(id=loja_id)
            print(loja)
            cliente = Cliente.objects.get(id=cliente_id)

            pedido = Pedido.objects.create(
                cliente=cliente,
                loja=loja,
                total=session.amount_total / 100,  # Convert from cents
                status='pendente',
                pagamento='reais',
                localizacao=request.session.get('endereco')
            )
            
            line_items = stripe.checkout.Session.list_line_items(session.id)
            for item in line_items.data:
                produto = Produto.objects.get(nome=item.description)
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=produto,
                    quantidade=item.quantity,
                    preco_unitario=produto.preco
                )

            # Chamando a função enviar_email_pedido com o request
            enviar_email_pedido(request, pedido, ItemPedido.objects.filter(pedido=pedido))
            keys_to_delete = ['carrinho', 'endereco', 'loja_id', 'cliente_id', 'total_geral_carrinho', 'total_pontos_carrinho']
            for key in keys_to_delete:
                if key in session:
                    del session[key]
            messages.success(request, 'Pedido criado com sucesso!')
            return redirect('pedido_pagamento', pedido_id=pedido.id)
        else:
            messages.error(request, 'Pagamento não foi aprovado.')
            return redirect('home')
    else:
        messages.error(request, 'Nenhuma sessão de pagamento encontrada.')
        return redirect('home')





def pedido_detalhe(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)  # Substitua Pedido pelo seu modelo de pedido se for diferente
    return render(request, 'core/pedido_detalhe.html', {'pedido': pedido})   
def strip_tags(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    text_content = soup.get_text()
    return text_content

def exibir_pedido(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)  # Obtenha o pedido usando o ID
    if request.method == "POST":
        if 'aceitar' in request.POST:
            # Implemente a lógica para aceitar o pedido
            return redirect('alguma_url_de_sucesso')
        elif 'recusar' in request.POST:
            # Implemente a lógica para recusar o pedido
            return redirect('alguma_url_de_falha')
    return render(request, 'core/pedido_detalhe.html', {'pedido': pedido})

def enviar_webhook_pedido(pedido):
    url = f"http://meusite.com/revisar-pedido/{pedido.id}"
    headers = {'Content-Type': 'application/json'}
    # Adicione aqui mais dados se necessário
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print("Webhook enviado com sucesso")
    else:
        print("Falha ao enviar webhook")
        
def gerar_token_aleatorio():
    return secrets.token_urlsafe(32)  # Gera um token seguro

def gerar_token(pedido, tipo):
    token_obj, created = TokenPedido.objects.get_or_create(
        pedido=pedido,
        tipo=tipo,
        defaults={
            'token': gerar_token_aleatorio(),  # Use a função real aqui
            'expiracao': timezone.now() + timedelta(days=1)  # Token expira em 1 dia
        }
    )
    if not created and token_obj.expiracao <= timezone.now():
        # Se o token existe mas expirou, gere um novo e atualize a expiração
        token_obj.token = gerar_token_aleatorio()
        token_obj.expiracao = timezone.now() + timedelta(days=1)
        token_obj.save()
    return token_obj.token

    
def enviar_email_pedido(request, pedido, itens_pedido, subperfil_nome=None):
    try:
        subject = 'Detalhes do Seu Pedido'
        context = {
            'pedido': pedido,
            'loja': pedido.loja,
            'itens_pedido': itens_pedido,
            'pedido_url': f'https://seu_dominio/pedido/{pedido.id}',  # Atualize com seu domínio real
            'subperfil_nome': subperfil_nome
        }

        html_content = render_to_string('core/email_pedido_detalhe.html', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(subject, text_content, 'augusto.dataanalysis@gmail.com', [pedido.loja.email])
        email.attach_alternative(html_content, "text/html")

        # Carregar a imagem diretamente
        image_path = os.path.join(settings.BASE_DIR, 'static/img/dev122062_faz_uma_logo_parecida_com_ifood_para_uma_plataforma_c_a6720ce1-23ea-425a-9b63-d7921326b252 (1).png')
        image_cid = 'image_cid'
        with open(image_path, 'rb') as img:
            mime_image = MIMEImage(img.read())
            mime_image.add_header('Content-ID', f'<{image_cid}>')
            email.attach(mime_image)

        email.send()
        recusar_pedido_automaticamente.apply_async((pedido.id,), countdown=600)  # 600 segundos = 10 minutos
        print("Email com detalhes do pedido enviado com sucesso.")
        logger.info(f"Tarefa de recusa automática agendada para o pedido {pedido.id}.")
    except Exception as e:
        print(f"Erro ao enviar email: {str(e)}")


def emitir_nota_fiscal_focus(cnpj_prestador, inscricao_municipal, codigo_municipio_prestador):
    token_homologacao_empresa = "xkRivLik9Wn4xbk4EaHq17d15L4vCtDO"
    url = "https://homologacao.focusnfe.com.br/v2/nfse?ref=001"

    # Dados fictícios para teste
    data = {
        "data_emissao": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "habilita_nfse": True,
        "prestador": {
            "cnpj": cnpj_prestador,
            "inscricao_municipal": inscricao_municipal,
            "codigo_municipio": codigo_municipio_prestador
        },
        "tomador": {
            "cnpj": "07504505000132",
            "razao_social": "Acras Tecnologia da Informação LTDA",
            "email": "contato@focusnfe.com.br",
            "endereco": {
                "logradouro": "Rua Dias da Rocha Filho",
                "numero": "999",
                "complemento": "Prédio 04 - Sala 34C",
                "bairro": "Alto da XV",
                "codigo_municipio": "4106902",
                "uf": "PR",
                "cep": "80045165"
            }
        },
        "servico": {
            "aliquota": 3,
            "discriminacao": "Nota fiscal referente a serviços prestados",
            "iss_retido": "false",
            "item_lista_servico": "0107",
            "codigo_tributario_municipio": "620910000",
            "valor_servicos": 1.0
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    print("Dados enviados para a API:")
    print(json.dumps(data, indent=4))

    try:
        response = requests.post(url, headers=headers, auth=(token_homologacao_empresa, ''), data=json.dumps(data))
        response.raise_for_status()

        if response.status_code in [201, 202]:
            nfse_data = response.json()
            if response.status_code == 201:
                nfse_url = nfse_data["caminho_danfe"]
                nfse_id = nfse_data["numero"]

                # Adicione aqui a lógica para salvar o URL e ID da NFS-e emitida

                return nfse_url
            else:
                print("Nota fiscal enviada para processamento. Consulte posteriormente para verificar o status.")
                return None
        else:
            print(f"Erro ao emitir NFS-e: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        if e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response headers: {e.response.headers}")
            print(f"Response content: {e.response.text}")
        else:
            print(f"Request exception: {str(e)}")
        raise
    except Exception as e:
        print(f"Erro inesperado ao emitir NFS-e: {str(e)}")
        raise

# Chamar a função para teste com CNPJ configurável
# Chamar a função para teste com CNPJ configurável

def confirmar_pagamento1(request):
    session_id = request.session.get('stripe_session_id')
    if session_id:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == 'paid':
            loja_id = request.session.get('loja_id')
            cliente_id = request.user.id  # Assuming the user ID is the customer ID

            loja = Loja.objects.get(id=loja_id)
            cliente = Cliente.objects.get(id=cliente_id)

            pedido = Pedido.objects.create(
                cliente=cliente,
                loja=loja,
                total=session.amount_total / 100,  # Convert from cents
                status='pendente',
                pagamento='reais',
                localizacao=request.session.get('endereco')
            )
            
            # Iterate over cart items again or use stored info in session
            for item in session.line_items:
                produto = Produto.objects.get(nome=item['name'])
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=produto,
                    quantidade=item['quantity'],
                    preco_unitario=produto.preco
                )

            enviar_email_pedido(request, pedido)
            messages.success(request, 'Pedido criado com sucesso!')
            return redirect('pedido_pagamento', pedido_id=pedido.id)
        else:
            messages.error(request, 'Pagamento não foi aprovado.')
            return redirect('home')
    else:
        messages.error(request, 'Nenhuma sessão de pagamento encontrada.')
        return redirect('home')



from django.http import JsonResponse

def verificar_status_pedido(request, pedido_id):
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        return JsonResponse({'status': pedido.status})
    except Pedido.DoesNotExist:
        return JsonResponse({'error': 'Pedido não encontrado'}, status=404)



def pedido_pagamento(request, pedido_id):
    try:
        cliente = request.user.cliente
    except:
        cliente = None
    pedido = get_object_or_404(Pedido, id=pedido_id)
    context = {
        'pedido': pedido,
        'cliente':cliente
    }
    return render(request, 'core/pedido_pendente.html', context)
@login_required
def pagar_com_pontos(request):
    carrinho = request.session.get('carrinho', {'itens': {}})
    endereco = request.POST.get('endereco')

    if not carrinho['itens']:
        messages.error(request, "Seu carrinho está vazio.")
        return redirect('carrinho')

    cliente = request.user.cliente
    total_geral_carrinho = Decimal('0.00')  # Inicializando como Decimal

    for item_id, item in carrinho['itens'].items():
        produto = Produto.objects.get(id=item_id)
        quantidade = int(item['quantidade'])
        preco = Decimal(item['preco'])
        total_geral_carrinho += preco * quantidade

    # Convertendo o total do carrinho em reais para pontos
    # Cada ponto vale R$0.4, então o total de pontos necessário é total em reais dividido por 0.4
    total_pontos_necessarios = total_geral_carrinho / Decimal('0.4')

    if cliente.pontos >= total_pontos_necessarios:
        pedido = Pedido.objects.create(
            cliente=cliente,
            loja=produto.categoria.loja,  # A loja pode ser acessada diretamente do primeiro produto
            pagamento='pontos',
            localizacao=endereco,
            total=total_geral_carrinho,
            status='pendente',
        )

        # Criando os itens do pedido
        itens_pedido = []
        for item_id, item in carrinho['itens'].items():
            produto = Produto.objects.get(id=item_id)
            item_pedido = ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                quantidade=quantidade,
                preco_unitario=preco
            )
            itens_pedido.append(item_pedido)

        # Atualizar os pontos do cliente
        cliente.pontos -= total_pontos_necessarios
        cliente.save()

        # Enviar email com os detalhes do pedido
        enviar_email_pedido(request, pedido, itens_pedido)
        #channel_layer = get_channel_layer()
        #async_to_sync(channel_layer.group_send)(
        #    f'pedido_{loja.id}',  # Nome do grupo é o ID da loja
        #    {
        #        'type': 'pedido_message',
        #        'message': f'Novo pedido {pedido.id} confirmado para sua loja.'
        #    }
        #)
        # Limpar o carrinho na sessão após a compra
        del request.session['carrinho']

        messages.success(request, "Pedido realizado com sucesso! Aguardando confirmação da loja.")
        return redirect('pedido_pagamento', pedido_id=pedido.id)  # Redirecione para a página que você considera apropriada
    else:
        messages.error(request, "Você não tem pontos suficientes para completar esta compra.")
        return redirect('carrinho')
def aceitar_pedido(request, pedido_id, token):
    logger.debug("Recebendo token...")
    logger.debug(f"Token recebido: {token}")

    if not token:
        logger.error("Token não fornecido.")
        return HttpResponse("Token não fornecido.", status=400)

    token_obj = TokenPedido.objects.filter(token=token, tipo='aceite', expiracao__gt=timezone.now(), pedido__id=pedido_id).first()
    if not token_obj:
        logger.error("Token inválido ou expirado.")
        return HttpResponse("Token inválido ou expirado.", status=400)

    pedido = token_obj.pedido
    if pedido.status != 'pendente':
        logger.error("Pedido não está pendente.")
        return HttpResponse("Pedido já foi processado.", status=400)

    # Verificação do método de pagamento
    if pedido.pagamento != 'pontos':
        # Lógica de atualização de saldo para pagamentos que não são com pontos
        percentual_para_loja = Decimal('0.85')
        valor_a_transferir = pedido.total * percentual_para_loja
        pedido.loja.saldo += valor_a_transferir
        pedido.loja.save()
        logger.info(f"Pedido {pedido_id} aceito com sucesso. R${valor_a_transferir} transferidos para a loja.")

    # Confirmar pedido
    pedido.status = 'confirmado'
    pedido.save()
    token_obj.delete()

    pedido.cliente.pontos += pedido.pontos
    pedido.cliente.save()

    messages.success(request, 'Pedido aceito com sucesso!')
    return redirect('home')


        
def revisar_pedido(request, pedido_id, acao):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    token_para_aceitar = gerar_token(pedido, 'aceite')
    token_para_recusar = gerar_token(pedido, 'recusa')
    if acao == 'aceitar':
        return redirect(reverse('aceitar_pedido', args=[pedido_id, token_para_aceitar]))
    elif acao == 'recusar':
        return redirect(reverse('recusar_pedido', args=[pedido_id, token_para_recusar]))
    else:
        # Handle unexpected action
        return HttpResponse("Ação inválida.", status=400)

    return render(request, 'core/confirmar_acao.html', {
        'pedido': pedido,
        'acao': acao,
        'token_para_aceitar': token_para_aceitar,
        'token_para_recusar': token_para_recusar
    })

@login_required
def recusar_pedido(request, pedido_id, token):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'erro', 'mensagem': 'Usuário não autenticado'}, status=403)
    
    token_obj = TokenPedido.objects.filter(token=token, tipo='recusa', expiracao__gt=timezone.now(), pedido__id=pedido_id).first()
    if not token_obj:
        return JsonResponse({'status': 'erro', 'mensagem': 'Token inválido ou expirado'}, status=400)

    pedido = get_object_or_404(Pedido, id=pedido_id)
    if pedido.status != 'pendente':
        return JsonResponse({'status': 'erro', 'mensagem': 'Pedido não está em estado pendente'}, status=400)

    # Se o pagamento foi feito com pontos
    if pedido.pagamento == 'pontos':
        pedido.status = 'recusado'
        pedido.save()
        token_obj.delete()
        return JsonResponse({'status': 'recusado', 'mensagem': 'Pedido recusado com sucesso'}, status=200)

    # Realiza o reembolso para pagamentos que não são com pontos
    try:
        refund = stripe.Refund.create(payment_intent=pedido.payment_id)
        pedido.status = 'recusado'
        pedido.save()
        token_obj.delete()
        messages.success(request, 'Pedido recusado e pagamento reembolsado com sucesso')
        return redirect('home')
    except stripe.error.StripeError as e:
        messages.error(request, 'Erro ao reembolsar o pagamento')
        return redirect('home')



def pedidos_cliente(request):
    try:
        cliente = request.user.cliente
    except:
        cliente = None
        
    if cliente is None:
        return redirect('home')  # Certifique-se de que 'home' é o nome correto da sua URL para a página inicial

    # Ordena os pedidos pelo campo 'data' em ordem decrescente
    pedidos = Pedido.objects.filter(cliente=cliente).prefetch_related('itempedido_set').order_by('-data')
    
    context = {
        'pedidos': pedidos,
        'cliente': cliente
    }
    return render(request, 'core/pedidos_cliente.html', context)


    
def checkout(request):
    carrinho = request.session.get('carrinho', {'itens': {}})
    cliente = request.user.cliente if request.user.is_authenticated and hasattr(request.user, 'cliente') else None
    subperfil_nome = None
    try:
        subperfil_id = request.session.get('subperfil_id')
    except:
        subperfil_id = None
    subperfil = None
    if subperfil_id:
        subperfil = get_object_or_404(Subperfil, id=subperfil_id, titular=cliente)
    endereco = cliente.endereco if cliente else None
    total_geral_carrinho = Decimal('0.00')
    total_frete = Decimal('0.00')
    loja = None
    itens_completos = []

    for produto_id, item in carrinho.get('itens', {}).items():
        produto = get_object_or_404(Produto, id=item['produto_id'])  # Corrigido para obter o produto corretamente
        try:
            loja = produto.categoria.loja
        except:
            loja = None
        item['imagem_url'] = produto.foto.url if produto.foto else None
        item['nome'] = produto.nome  # Já deve estar definido, mas só para garantir
        preco = Decimal(item['preco'])
        quantidade = item['quantidade']
        if not item['promocao']:  # Apenas adicionar o preço se não for promoção
            total_geral_carrinho += preco * quantidade
        itens_completos.append(item)  # Adiciona o item atualizado à lista

    if loja:
        total_frete = loja.valor_frete

    total_geral_com_frete = total_geral_carrinho + total_frete

    return render(request, 'core/checkout_test.html', {
        'itens': itens_completos,  # Passa os itens atualizados para o template
        'cliente': cliente,
        'endereco': endereco,
        'total_geral': total_geral_carrinho,
        'total_frete': total_frete,
        'total_geral_com_frete': total_geral_com_frete,
        'loja': loja,
        'subperfil': subperfil
    })

def search(request):
    query = request.GET.get('query', '')
    try:
        cliente = request.user.cliente
    except AttributeError:
        cliente = None

    produtos_list = []
    lojas_list = []

    if query and cliente and cliente.endereco:
        latitude = cliente.endereco.latitude
        longitude = cliente.endereco.longitude

        if latitude is not None and longitude is not None:
            produtos = Produto.objects.filter(nome__icontains=query)
            lojas = Loja.objects.filter(nomeLoja__icontains=query)

            for produto in produtos:
                loja = produto.categoria.loja
                if loja and loja.endereco and loja.endereco.latitude and loja.endereco.longitude:
                    distancia = haversine(float(longitude), float(latitude), float(loja.endereco.longitude), float(loja.endereco.latitude))
                    if distancia <= 100:
                        produtos_list.append({
                            'id': produto.id,
                            'nome': produto.nome,
                            'foto': produto.foto.url if produto.foto else None
                        })

            for loja in lojas:
                if loja.endereco and loja.endereco.latitude and loja.endereco.longitude:
                    distancia = haversine(float(longitude), float(latitude), float(loja.endereco.longitude), float(loja.endereco.latitude))
                    if distancia <= 100:
                        lojas_list.append({
                            'id': loja.id,
                            'nomeLoja': loja.nomeLoja,
                            'foto': loja.foto.url if loja.foto else None
                        })

    return JsonResponse({
        'produtos': produtos_list,
        'lojas': lojas_list,
    })
def search_results(request):
    query = request.GET.get('query', '')
    produtos = Produto.objects.filter(nome__icontains=query)
    lojas = Loja.objects.filter(nomeLoja__icontains=query)

    context = {
        'query': query,
        'produtos': produtos,
        'lojas': lojas
    }

    return render(request, 'core/search_results.html', context)


#def cartao(request):
#    publicKey = getPublicKey()
#    context = {
#        'publicKey':publicKey
#    }
#    return render(request, 'core/cartao.html', context)
def pagar_com_pix(request):
    carrinho = request.session.get('carrinho', {'itens': {}})
    cliente = request.user.cliente if request.user.is_authenticated and hasattr(request.user, 'cliente') else None
    endereco = cliente.endereco if cliente else None
    total_geral_carrinho = Decimal('0.00')
    total_frete = Decimal('0.00')
    loja = None
    # Aqui, vamos garantir que a imagem_url está sendo passada corretamente
    itens_completos = []
    for produto_id, item in carrinho.get('itens', {}).items():
        produto = get_object_or_404(Produto, id=produto_id)
        try:
            loja = produto.categoria.loja
        except:
            loja = None
        item['imagem_url'] = produto.foto.url if produto.foto else None
        item['nome'] = produto.nome  # Já deve estar definido, mas só para garantir
        preco = Decimal(item['preco'])
        quantidade = item['quantidade']
        total_geral_carrinho += preco * quantidade
        frete = loja.valor_frete
        total_frete += total_geral_carrinho + frete
        itens_completos.append(item)  # Adiciona o item atualizado à lista

    return render(request, 'core/pix.html', {
        'itens': itens_completos,  # Passa os itens atualizados para o template
        'cliente': cliente,
        'endereco': endereco,
        'total_geral': total_geral_carrinho,
        'total_frete': total_frete,
        'loja':loja
    })