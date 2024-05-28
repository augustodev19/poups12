from celery import shared_task
import requests
from usuarios.models import *
import stripe
from django.utils import timezone
import time

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

API_URL = "https://api.openpix.com.br/api/v1/charge"
HEADERS = {'Authorization': "Q2xpZW50X0lkX2NjNjFiMmI0LWE1N2QtNGE1My05NmVkLWZmOWYyZTFjYjQ0NzpDbGllbnRfU2VjcmV0X1h5b2NuR3hPN0VrRk41aHpzdjg0bTE3ajNHbUpqeWNrbXdoejhBbFUzTTA9"}
@shared_task(bind=True)
def check_charge_status(self, correlation_id, start_time=None):
    print(f"Tarefa agendada para verificar o status da cobrança com correlation_id {correlation_id}")
    try:
        charge = Charge.objects.get(correlation_id=correlation_id)

        if start_time is None:
            start_time = timezone.now().isoformat()

        # URL correta para verificar o status da cobrança
        api_url = f"{API_URL}/{correlation_id}"
        print(f"Verificando status da cobrança na URL: {api_url}")

        response = requests.get(api_url, headers=HEADERS)
        print(f"Resposta da API: {response.status_code}, {response.text}")

        if response.status_code == 404:
            print(f"Recurso não encontrado para o correlation_id {correlation_id}")
            charge.last_error = f"Recurso não encontrado para o correlation_id {correlation_id}"
            charge.save()
            return

        try:
            charge_data = response.json()
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")
            charge.last_error = f"Erro ao decodificar JSON: {e}"
            charge.save()
            return

        if 'charge' in charge_data and charge_data['charge']['status'] == 'COMPLETED':
            print(f"Cobrança com correlation_id {correlation_id} completada.")
            charge.status = 'completed'
            charge.save()
            handle_pix_payment(correlation_id)
        else:
            elapsed_time = timezone.now() - timezone.datetime.fromisoformat(start_time)
            if elapsed_time < timezone.timedelta(minutes=10):
                print(f"Tentativa {charge.attempts + 1} para cobrança com correlation_id {correlation_id}. Status atual: {charge_data.get('charge', {}).get('status')}")
                charge.attempts += 1
                charge.save()
                print(f"Re-agendando tarefa para verificar o status da cobrança com correlation_id {correlation_id} em 3 segundos")
                self.apply_async((correlation_id, start_time), countdown=3)
            else:
                print(f"Tentativas para cobrança com correlation_id {correlation_id} esgotadas após 10 minutos.")
                charge.status = 'failed'
                charge.save()

    except Charge.DoesNotExist:
        print(f"Charge com correlation_id {correlation_id} não encontrada.")
    except Exception as e:
        print(f"Erro ao verificar o status da cobrança com correlation_id {correlation_id}: {str(e)}")
        charge.last_error = str(e)
        charge.save()