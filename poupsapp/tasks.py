from celery import shared_task
import requests
from usuarios.models import *
import stripe
from django.utils import timezone
import time
from main.views import *
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.cache import cache
import json
from decimal import Decimal

#logger = logging.getLogger(__name__)
API_URL = "https://api.openpix.com.br/api/v1/charge"
HEADERS = {'Authorization': "Q2xpZW50X0lkX2NjNjFiMmI0LWE1N2QtNGE1My05NmVkLWZmOWYyZTFjYjQ0NzpDbGllbnRfU2VjcmV0X1h5b2NuR3hPN0VrRk41aHpzdjg0bTE3ajNHbUpqeWNrbXdoejhBbFUzTTA9"}
@shared_task(bind=True)
def test_func(self):
    for i in range(10):
        print(i)
    return "Done"

@shared_task(bind=True)
def recusar_pedido_automaticamente(self, pedido_id):
    print(f"Tarefa de recusa automática iniciada para o pedido {pedido_id}")

    try:
        pedido = Pedido.objects.get(id=pedido_id)
        if pedido.status != 'pendente':
            print(f"Pedido {pedido_id} já processado com status {pedido.status}")
            return

        # Se o pagamento foi feito com pontos
        if pedido.pagamento == 'pontos':
            pedido.status = 'recusado'
            pedido.save()
            print(f"Pedido {pedido_id} recusado com pontos.")
            return

        # Realiza o reembolso para pagamentos que não são com pontos
        try:
            stripe.Refund.create(payment_intent=pedido.payment_id)
            pedido.status = 'recusado'
            pedido.save()
            print(f"Pedido {pedido_id} recusado e reembolsado com sucesso.")
        except stripe.error.StripeError as e:
            print(f"Erro ao reembolsar o pagamento para o pedido {pedido_id}: {str(e)}")
    except Pedido.DoesNotExist:
        print(f"Pedido {pedido_id} não encontrado.")
    except Exception as e:
        print(f"Erro ao processar a recusa automática para o pedido {pedido_id}: {str(e)}")

@shared_task(bind=True)
def check_charge_status(self, correlation_id, start_time=None):
    print('verificando')
    #logger.warning(f"Tarefa agendada para verificar o status da cobrança com correlation_id {correlation_id}")
    try:
        charge = Charge.objects.get(correlation_id=correlation_id)

        if start_time is None:
            start_time = timezone.now().isoformat()

        api_url = f"{API_URL}/{correlation_id}"
        print(f"Verificando status da cobrança na URL: {api_url}")

        response = requests.get(api_url, headers=HEADERS)
        #logger.warning(f"Resposta da API: {response.status_code}, {response.text}")

        if response.status_code == 404:
            logger.warning(f"Recurso não encontrado para o correlation_id {correlation_id}")
            charge.last_error = f"Recurso não encontrado para o correlation_id {correlation_id}"
            charge.save()
            return

        try:
            charge_data = response.json()
        except json.JSONDecodeError as e:
            #logger.warning(f"Erro ao decodificar JSON: {e}")
            charge.last_error = f"Erro ao decodificar JSON: {e}"
            charge.save()
            return

        if 'charge' in charge_data and charge_data['charge']['status'] == 'COMPLETED':
            #logger.warning(f"Cobrança com correlation_id {correlation_id} completada.")
            charge.status = 'completed'
            charge.save()
            handle_pix_payment.delay(correlation_id)
        else:
            elapsed_time = timezone.now() - timezone.datetime.fromisoformat(start_time)
            if elapsed_time < timezone.timedelta(minutes=10):
                #logger.warning(f"Tentativa {charge.attempts + 1} para cobrança com correlation_id {correlation_id}. Status atual: {charge_data.get('charge', {}).get('status')}")
                charge.attempts += 1
                charge.save()
                #logger.warning(f"Re-agendando tarefa para verificar o status da cobrança com correlation_id {correlation_id} em 3 segundos")
                self.apply_async((correlation_id, start_time), countdown=3)
            else:
                #logger.warning(f"Tentativas para cobrança com correlation_id {correlation_id} esgotadas após 10 minutos.")
                charge.status = 'failed'
                charge.save()

    except Charge.DoesNotExist:
        pass
        #logger.warning(f"Charge com correlation_id {correlation_id} não encontrada.")
    except Exception as e:
        charge.last_error = str(e)
        #logger.warning(f"Erro ao verificar o status da cobrança com correlation_id {correlation_id}: {str(e)}")
        charge.save()



@shared_task(bind=True)
def handle_pix_payment(self, correlation_id):
    try:
        charge = Charge.objects.get(correlation_id=correlation_id)
        if charge.status == 'completed':
            total_geral_carrinho = Decimal(charge.total)
            loja_id = charge.loja_id
            cliente_id = charge.cliente_id
            charge_endereco = charge.endereco if charge.endereco else None
            retirada_loja = charge.retirada_na_loja

            cliente = Cliente.objects.get(id=cliente_id)
            loja = Loja.objects.get(id=loja_id)
            codigo_secreto = str(uuid.uuid4())
            pedido = Pedido.objects.create(
                cliente=cliente,
                loja=loja,
                total=total_geral_carrinho,
                pontos=int(total_geral_carrinho * Decimal('0.4')),
                status='pendente',
                pagamento='pix',
                payment_id=correlation_id,
                localizacao=charge_endereco,
                retirada_na_loja=retirada_loja,
                correlation_id=correlation_id,
                codigo_secreto=codigo_secreto
            )

            carrinho = cache.get(f'carrinho_{charge.cliente_id}', {'itens': {}, 'pontos_para_proxima_promocao': {}})

            for item_key, item in carrinho['itens'].items():
                if item_key.startswith('promocao_'):
                    continue

                produto = Produto.objects.get(id=item['produto_id'])
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=produto,
                    quantidade=item['quantidade'],
                    preco_unitario=Decimal(item['preco'])
                )

            enviar_email_pedido_pix.delay(pedido.id)
            enviar_notificacao_pedido_pix.delay(pedido.id)
            cache.set(f"pedido_id_{correlation_id}", pedido.id, timeout=300)
            charge.payment_status = 'completed'
            charge.save()
            return pedido.id
        else:
            charge.payment_status = 'failed'
            charge.save()
            return None
    except Exception as e:
        charge.payment_status = 'error'
        charge.save()
        raise e

@shared_task(bind=True)
def enviar_email_pedido_pix(self, pedido_id, subperfil_nome=None):
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        itens_pedido = pedido.itempedido_set.all()
        itens_promocionais = [item for item in itens_pedido if item.produto.promocao]

        subject = 'Detalhes do Seu Pedido'
        context = {
            'pedido': pedido,
            'loja': pedido.loja,
            'itens_pedido': itens_pedido,
            'itens_promocionais': itens_promocionais,
            'pedido_url': f'https://poupecomprando.com.br/pedido/{pedido.id}',  # Atualize com seu domínio real
            'subperfil_nome': subperfil_nome
        }

        html_content = render_to_string('core/email_pedido_detalhe.html', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(subject, text_content, 'augusto.dataanalysis@gmail.com', [pedido.loja.email])
        email.attach_alternative(html_content, "text/html")

        email.send()
        recusar_pedido_automaticamente.apply_async((pedido.id,), countdown=600)
        logger.warning("Email com detalhes do pedido enviado com sucesso.")
    except Exception as e:
        pass
        #logger.warning(f"Erro ao enviar email: {str(e)}")

@shared_task(bind=True)
def enviar_notificacao_pedido_pix(self, pedido_id, subperfil_nome=None):
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        itens_pedido = pedido.itempedido_set.all()
        message = {
            'pedido_id': pedido.id,
            'loja': pedido.loja.nomeLoja,
            'itens_pedido': [f'{item.produto.nome} - Quantidade: {item.quantidade}, Preço: R${item.preco_unitario}' for item in itens_pedido],
            'itens_promocionais': [f'{item.produto.nome} - Quantidade: {item.quantidade}, Preço: Promoção' for item in itens_pedido if item.promocao],
            'total': pedido.total,
            'subperfil_nome': subperfil_nome or pedido.cliente.nome,
            'cliente': pedido.cliente.nome,
            'cpf': pedido.cliente.username,
            'telefone': pedido.cliente.telefone,
            'tempo_entrega_min': pedido.loja.tempo_entrega_min or 60,
            'tempo_entrega_max': pedido.loja.tempo_entrega_max or 75
        }

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'pedidos_{pedido.loja.id}',  # Grupo específico do lojista
            {
                'type': 'pedido_message',
                'message': message
            }
        )
        print("Notificação de pedido enviada com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao enviar notificação: {str(e)}")
        raise

@shared_task(bind=True)
def verificar_pagamento_concluido(self, correlation_id, start_time=None):
    if start_time is None:
        start_time = timezone.now().isoformat()

    status = cache.get(f'pix_payment_status_{correlation_id}')
    if status == 'completed':
        return True
    elif status in ['failed', 'error']:
        return False
    else:
        elapsed_time = timezone.now() - timezone.datetime.fromisoformat(start_time)
        if elapsed_time < timezone.timedelta(minutes=10):
            self.apply_async((correlation_id, start_time), countdown=3)
        else:
            return False

@shared_task(bind=True)
def check_credito_pix_status(self, correlation_id, start_time=None):
    print('verificando status de compra de crédito via PIX')
    try:
        charge = Charge.objects.get(correlation_id=correlation_id)

        if start_time is None:
            start_time = timezone.now().isoformat()

        api_url = f"{API_URL}/{correlation_id}"
        print(f"Verificando status da cobrança na URL: {api_url}")

        response = requests.get(api_url, headers=HEADERS)
        print(f"Resposta da API: {response.status_code}, {response.text}")

        if response.status_code == 404:
            charge.last_error = f"Recurso não encontrado para o correlation_id {correlation_id}"
            charge.save()
            return

        try:
            charge_data = response.json()
        except json.JSONDecodeError as e:
            charge.last_error = f"Erro ao decodificar JSON: {e}"
            charge.save()
            return

        if 'charge' in charge_data and charge_data['charge']['status'] == 'COMPLETED':
            charge.status = 'completed'
            charge.save()
            handle_credito_pix_payment.delay(correlation_id)
        else:
            elapsed_time = timezone.now() - timezone.datetime.fromisoformat(start_time)
            if elapsed_time < timezone.timedelta(minutes=10):
                charge.attempts += 1
                charge.save()
                self.apply_async((correlation_id, start_time), countdown=3)
            else:
                charge.status = 'failed'
                charge.save()

    except Charge.DoesNotExist:
        print(f"Charge com correlation_id {correlation_id} não encontrada.")
    except Exception as e:
        charge.last_error = str(e)
        charge.save()


@shared_task(bind=True)
def handle_credito_pix_payment(self, correlation_id):
    try:
        charge = Charge.objects.get(correlation_id=correlation_id)
        if charge.status == 'completed':
            cliente = Cliente.objects.get(id=charge.cliente_id)
            pontos_a_adicionar = Decimal(charge.pontos_a_adicionar)

            cliente.pontos += pontos_a_adicionar
            cliente.save()

            charge.payment_status = 'completed'
            charge.save()

            # Enviar notificação ou email confirmando a adição de pontos
            enviar_email_credito_confirmado.delay(cliente.id, pontos_a_adicionar)
            return True
        else:
            charge.payment_status = 'failed'
            charge.save()
            return False
    except Exception as e:
        charge.payment_status = 'error'
        charge.save()
        raise e