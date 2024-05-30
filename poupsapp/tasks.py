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
    #logger.warning(f"Tarefa agendada para verificar o status da cobrança com correlation_id {correlation_id}")
    try:
        charge = Charge.objects.get(correlation_id=correlation_id)

        if start_time is None:
            start_time = timezone.now().isoformat()

        api_url = f"{API_URL}/{correlation_id}"
        logger.warning(f"Verificando status da cobrança na URL: {api_url}")

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
    #logger.warning(f"Iniciando processamento do pagamento Pix para correlation_id {correlation_id}")
    try:
        charge = Charge.objects.get(correlation_id=correlation_id)
        if charge.status == 'completed':
            total_geral_carrinho = Decimal(charge.total)
            loja_id = charge.loja_id
            cliente_id = charge.cliente_id
            charge_endereco = charge.endereco if charge.endereco else None
            
            #logger.warning(f"Cliente ID: {cliente_id}, Loja ID: {loja_id}, Total: {total_geral_carrinho}")

            cliente = Cliente.objects.get(id=cliente_id)
            loja = Loja.objects.get(id=loja_id)

            #logger.warning(f"Criando pedido para o cliente {cliente_id} na loja {loja_id} com total de {total_geral_carrinho}")

            pedido = Pedido.objects.create(
                cliente=cliente,
                loja=loja,
                total=total_geral_carrinho,
                pontos=int(total_geral_carrinho * Decimal('0.4')),  # Corrigido para usar Decimal e converter para int
                status='pendente',
                pagamento='pix',
                payment_id=correlation_id,
                localizacao=charge_endereco
            )

            carrinho = cache.get(f'carrinho_{charge.cliente_id}', {'itens': {}, 'pontos_para_proxima_promocao': {}})
            #logger.warning(f"Carrinho recuperado do cache: {carrinho}")

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
            #logger.warning(f"Pedido criado com sucesso para o cliente {cliente_id}")

            enviar_email_pedido_pix.delay(pedido.id)
            cache.set(f"pedido_id_{correlation_id}", pedido.id, timeout=300)
            #logger.warning(f"Pedido ID salvo no cache: {cache.get(f'pedido_id_{correlation_id}')}")
            pedido_id = pedido.id
            if pedido_id:
                keys_to_delete = [
                    'preference_id', 'total_geral_carrinho', 'total_pontos_carrinho',
                    'carrinho', 'endereco', 'loja_id', 'cliente_id'
                ]
                # Limpeza da sessão
                for key in keys_to_delete:
                    if key in request.session:
                        del request.session[key]
                
                # Mensagem de sucesso
                messages.success(request, 'Pedido criado com sucesso!')
                return redirect('pedido_pagamento', pedido_id=pedido_id)
            else:
                messages.error(request, "Não foi possível encontrar o pedido.")
                return redirect('home')
        
    except Cliente.DoesNotExist:
        pass
        #logger.warning(f"Cliente ID {cliente_id} não encontrado.")
    except Loja.DoesNotExist:
        pass
        #logger.warning(f"Loja ID {loja_id} não encontrada.")
    except Produto.DoesNotExist:
        pass
        #logger.warning(f"Produto não encontrado.")
    except Exception as e:
        pass
        #logger.warning(f"Erro ao processar o pagamento Pix: {str(e)}")

@shared_task(bind=True)
def enviar_email_pedido_pix(self, pedido_id, subperfil_nome=None):
    #logger.warning(f"Iniciando envio de email para o pedido {pedido_id}")
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        itens_pedido = pedido.itempedido_set.all()
        subject = 'Detalhes do Seu Pedido'
        context = {
            'pedido': pedido,
            'loja': pedido.loja,
            'itens_pedido': itens_pedido,
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