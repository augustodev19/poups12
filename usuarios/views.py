from django.shortcuts import render, get_object_or_404
from usuarios.forms import *
from .models import *
from django.contrib.auth.decorators import login_required

from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import login as auth_login
from .forms import LoginForm
from django.contrib.auth import authenticate
import logging
from django.template.loader import render_to_string
from bs4 import BeautifulSoup

from django.db.models.functions import TruncMonth
from django.db.models.functions import TruncYear
import mercadopago
from django.core.mail import EmailMultiAlternatives


from django.utils.timezone import now, datetime
from django.db.models import Sum

from django.utils.http import urlencode
from django.urls import reverse
import googlemaps
from django.contrib import messages
from .forms import *
from geopy.geocoders import Nominatim
from django.contrib.auth import authenticate, login

# Configuração básica do logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def registerCliente(request):
    logger.debug("Iniciando o processo de registro do cliente")
    form = ClienteRegistrationForm()

    if request.method == 'POST':
        form = ClienteRegistrationForm(request.POST, request.FILES)
        logger.debug(f"Form POST recebido: {form}")

        if form.is_valid():
            logger.debug("Formulário é válido")
            user = Cliente.objects.create_user(
                nome=form.cleaned_data['nome'],
                username=form.cleaned_data['username'],
                telefone=form.cleaned_data['telefone'],
                email=form.cleaned_data['email'],
                foto=form.cleaned_data['foto'],
                password=form.cleaned_data['password1'],
            )
            user.save()
            logger.debug(f"Usuário criado: {user}")

            cep = request.POST.get('cep')
            numero = request.POST.get('numero')

            if cep:
                logger.debug(f"CEP recebido: {cep}")
                response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
                data = response.json()
                logger.debug(f"Resposta da API ViaCEP: {data}")

                if response.status_code == 200 and not data.get('erro'):
                    estado, _ = Estado.objects.get_or_create(nome=data['uf'])
                    cidade, _ = Cidade.objects.get_or_create(nome=data['localidade'], estado=estado)
                    bairro, _ = Bairro.objects.get_or_create(nome=data['bairro'], cidade=cidade)
                    cep_obj, _ = CEP.objects.get_or_create(codigo=cep)
                    endereco_completo = f"{data['logradouro']}, {data['bairro']}, {data['localidade']}, {data['uf']}, {data['cep']}"
                    latitude, longitude = obter_coordenadas(endereco_completo, "AIzaSyCBd2FPXoFej_0ooiHJfRjCZFzIADYSUIY")

                    endereco, _ = Endereco.objects.get_or_create(
                        rua=data['logradouro'],
                        bairro=bairro,
                        cidade=cidade,
                        estado=estado,
                        cep=cep_obj,
                        latitude=latitude,
                        longitude=longitude,
                        numero=numero
                    )
                    logger.debug(f"Endereço criado/obtido: {endereco}")

                    user.endereco = endereco
                    user.save()

            messages.success(request, 'Cadastro realizado com sucesso!')
            logger.debug("Cadastro realizado com sucesso, redirecionando para login")
            return redirect('login')
        else:
            logger.error(f"Formulário inválido: {form.errors}")
            messages.error(request, form.errors)

    return render(request, 'core/registroClientes.html', {'form': form})


def perfil_familia(request):
    return render(request, 'core/perfilFamilia.html')

def tipo_perfil(request):
    return render(request, 'core/tipoPerfil.html')

def create_subperfil(request):
    if request.method == 'POST':
        form = SubperfilForm(request.POST, request.FILES)
        if form.is_valid():
            subperfil = form.save(commit=False)
            if hasattr(request.user, 'cliente'):
                subperfil.titular = request.user.cliente
                if request.user.cliente.subperfis.count() < 4:
                    subperfil.save()
                    return redirect('subperfil_list')
                else:
                    form.add_error(None, 'Você não pode criar mais de 4 subperfis.')
            else:
                form.add_error(None, 'Usuário não é um cliente válido.')
    else:
        form = SubperfilForm()
    return render(request, 'core/create_subperfil.html', {'form': form})


def subperfil_list(request):
    try:
        cliente = request.user.cliente
    except:
        cliente = None
        messages.error(request, 'Cliente não encontrado.')
        return redirect('home')

    if hasattr(request.user, 'cliente'):
        subperfis = request.user.cliente.subperfis.all()
        context = {
            'subperfis':subperfis,
            'cliente':cliente
        }
        return render(request, 'core/subperfil_list.html', context)
    else:
        messages.error(request, 'Perfil família não acessível.')
        return redirect('home')

def select_subperfil(request, subperfil_id):
    subperfil = get_object_or_404(Subperfil, id=subperfil_id, titular=request.user.cliente)
    # Simulando login de subperfil
    request.session['subperfil_id'] = subperfil.id
    return redirect('home')


@login_required
def remove_subperfil(request, subperfil_id):
    subperfil = get_object_or_404(Subperfil, id=subperfil_id, titular=request.user.cliente)
    if subperfil.is_titular:
        messages.error(request, 'O subperfil do titular não pode ser excluído.')
        return redirect('subperfil_list')
    
    subperfil.delete()
    messages.success(request, 'Subperfil removido com sucesso.')
    return redirect('subperfil_list')

@login_required
def edit_subperfil(request, subperfil_id):
    subperfil = get_object_or_404(Subperfil, id=subperfil_id, titular=request.user.cliente)
    if request.method == 'POST':
        form = SubperfilForm(request.POST, request.FILES, instance=subperfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subperfil atualizado com sucesso.')
            return redirect('subperfil_list')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = SubperfilForm(instance=subperfil)
    
    context = {
        'form': form,
        'subperfil': subperfil
    }
    return render(request, 'core/edit_subperfil.html', context)

def selecionar_perfil(request):
    return render(request, 'core/perfisFamilia.html')

def selecionar_perfil(request):
    return render(request, 'core/perfisFamilia.html')

def registerFamilia(request):
    form = ClienteRegistrationForm()

    if request.method == 'POST':
        form = ClienteRegistrationForm(request.POST, request.FILES)
        
        if form.is_valid():
           
                user = Cliente.objects.create_user(
                    nome = form.cleaned_data['nome'],
                    username = form.cleaned_data['username'],
                    telefone = form.cleaned_data['telefone'],
                    email=form.cleaned_data['email'],
                    foto = form.cleaned_data['foto'],
                    password=form.cleaned_data['password1'],
                    plano_familia = True,
              
                 
                  
                )
                user.save()

                cep = request.POST.get('cep')
                complemento = request.POST.get('complemento')

                if cep:
                    response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
                    data = response.json()

                    if response.status_code == 200 and not data.get('erro'):
                        estado, _ = Estado.objects.get_or_create(nome=data['uf'])
                        cidade, _ = Cidade.objects.get_or_create(nome=data['localidade'], estado=estado)
                        bairro, _ = Bairro.objects.get_or_create(nome=data['bairro'], cidade=cidade)
                        cep_obj, _ = CEP.objects.get_or_create(codigo=cep)
                        endereco_completo = f"{data['logradouro']}, {data['bairro']}, {data['localidade']}, {data['uf']}, {data['cep']}"
                        latitude, longitude = obter_coordenadas(endereco_completo, "AIzaSyCBd2FPXoFej_0ooiHJfRjCZFzIADYSUIY")

                        endereco, _ = Endereco.objects.get_or_create(
                            rua=data['logradouro'],
                            complemento=complemento,
                            bairro=bairro,
                            cidade=cidade,
                            estado=estado,
                            cep=cep_obj,
                            latitude=latitude,
                            longitude=longitude
                        )

                        user.endereco = endereco
                        user.save()

             
               
               
                    
                messages.success(request, 'Cadastro Realizado com sucesso!')
                return redirect('login')
        else:
            messages.error(request, form.errors)
    
    return render(request, 'core/registroFamilia.html', {'form': form})

def obter_coordenadas(endereco_completo, google_maps_api_key):
    gmaps = googlemaps.Client(key=google_maps_api_key)
    geocode_result = gmaps.geocode(endereco_completo)
    
    if geocode_result:
        latitude = geocode_result[0]['geometry']['location']['lat']
        longitude = geocode_result[0]['geometry']['location']['lng']
        return latitude, longitude
    
    return None, None

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def registerLoja(request):
    logger.debug("Iniciando o processo de registro da loja")
    categorias = Categoria.objects.all()
    form = LojaRegistrationForm()

    if request.method == 'POST':
        form = LojaRegistrationForm(request.POST, request.FILES)
        logger.debug(f"Form POST recebido: {form}")

        if form.is_valid():
            logger.debug("Formulário é válido")
            user = Loja.objects.create_user(
                nomeLoja=form.cleaned_data['nomeLoja'],
                nome=form.cleaned_data['nome'],
                foto=form.cleaned_data['foto'],
                username=form.cleaned_data['username'],
                telefone=form.cleaned_data['telefone'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
            )
            logger.debug(f"Usuário criado: {user}")

            cep = request.POST.get('cep')
            complemento = request.POST.get('complemento')
            numero = request.POST.get('numero')

            if cep:
                logger.debug(f"CEP recebido: {cep}")
                response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
                data = response.json()
                logger.debug(f"Resposta da API ViaCEP: {data}")

                if response.status_code == 200 and not data.get('erro'):
                    estado, _ = Estado.objects.get_or_create(nome=data['uf'])
                    cidade, _ = Cidade.objects.get_or_create(nome=data['localidade'], estado=estado)
                    bairro, _ = Bairro.objects.get_or_create(nome=data['bairro'], cidade=cidade)
                    cep_obj, _ = CEP.objects.get_or_create(codigo=cep)
                    endereco_completo = f"{data['logradouro']}, {data['bairro']}, {data['localidade']}, {data['uf']}, {data['cep']}"
                    latitude, longitude = obter_coordenadas(endereco_completo, "AIzaSyCBd2FPXoFej_0ooiHJfRjCZFzIADYSUIY")

                    endereco, _ = Endereco.objects.get_or_create(
                        rua=data['logradouro'],
                        complemento=complemento,
                        bairro=bairro,
                        cidade=cidade,
                        estado=estado,
                        cep=cep_obj,
                        latitude=latitude,
                        longitude=longitude,
                        numero=numero
                    )
                    logger.debug(f"Endereço criado/obtido: {endereco}")

                    user.endereco = endereco
                    user.save()

                selected_categorias = form.cleaned_data['categorias']
                logger.debug(f"Categorias selecionadas: {selected_categorias}")
                user.categorias.set(selected_categorias)

                messages.success(request, 'Cadastro realizado com sucesso!')
                logger.debug("Cadastro realizado com sucesso, redirecionando para login")
                return redirect('login')
        else:
            logger.error(f"Formulário inválido: {form.errors}")
            messages.error(request, form.errors)
            return redirect('registerLoja')

    context = {'categorias': categorias}
    return render(request, 'core/registroEmpresas.html', context)

from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.shortcuts import render, redirect


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        cliente = None

        if user is not None:
            auth_login(request, user)
            try:
                cliente = request.user.cliente
            except:
                pass
            try: 
                loja = request.user.loja
            except:
                pass
            if cliente:
                if cliente.plano_familia:
                    messages.success(request, "Usuário logado com sucesso!")
                    return redirect('subperfil_list')
            elif loja:
                messages.success(request, "Lojista logado com sucesso!")
                return redirect('editar_loja')
            
            # Verifica se há itens no carrinho
            carrinho = request.session.get('carrinho', {'itens': {}})
            if carrinho['itens']:
                messages.success(request, "Usuário logado com sucesso!")
                return redirect('checkout')  # Redireciona para o checkout se houver itens no carrinho

            messages.success(request, "Usuário logado com sucesso!")
            return redirect(request.GET.get('next', 'home'))  # Redireciona para lojas próximas se o carrinho estiver vazio
        else:
            messages.error(request, "Email ou senha inválidos.")
    else:
        form = LoginForm()
        
    return render(request, 'core/login.html', {'form': form})


def tipo_cliente(request):
    return render(request, 'core/tipoCliente.html')
    
def editar_loja2(request):
    try:
        loja = request.user.loja    
    except Loja.DoesNotExist:
        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")

    if request.method == 'POST':
        form = LojaForm(request.POST, request.FILES, instance=loja)
        if form.is_valid():
            form.save()
            # Redirecionar para a página da loja ou alguma página de sucesso
    else:
        form = LojaForm(instance=loja)

    context = { 'loja':loja,
    'form':form,
    }

    return render(request, 'core/editar_loja.html', context)


    
def editar_cliente(request):
    try:
        cliente = request.user.cliente
    except Cliente.DoesNotExist:
        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")
    if cliente.plano_familia:
        return render('perfil_familia')
    if request.method == 'POST':
        form = EditarClienteForm(request.POST, request.FILES, instance=cliente)
        if form.is_valid():
            form.save()
            # Redirecionar para a página da loja ou alguma página de sucesso
    else:
        form = EditarClienteForm(instance=cliente)

    context = { 'cliente':cliente,
    'form':form,
    }

    return render(request, 'core/editar_perfil.html', context)

def get_sales_data(request):
    # Supõe-se que a loja do usuário esteja autenticada
    loja = request.user.loja

    # Agrupando os pedidos por mês
    monthly_totals = Pedido.objects.filter(loja=loja, data__year=timezone.now().year)\
                                   .annotate(month=TruncMonth('data'))\
                                   .values('month')\
                                   .annotate(total_sales=Sum('total'))\
                                   .order_by('month')

    months = [mt['month'].strftime('%B') for mt in monthly_totals]
    totals = [mt['total_sales'] or 0 for mt in monthly_totals]

    return months, totals


def get_annual_sales_data(request):
    # Supõe-se que a loja do usuário esteja autenticada
    loja = request.user.loja

    # Agrupando os pedidos por ano
    annual_totals = Pedido.objects.filter(loja=loja)\
                                  .annotate(year=TruncYear('data'))\
                                  .values('year')\
                                  .annotate(total_sales=Sum('total'))\
                                  .order_by('year')

    years = [at['year'].year for at in annual_totals]
    totals = [at['total_sales'] or 0 for at in annual_totals]

    return years, totals

def get_current_year_sales(request):
    loja = request.user.loja
    current_year = timezone.now().year
    total_sales_current_year = Pedido.objects.filter(
        loja=loja,
        data__year=current_year
    ).aggregate(total_sales=Sum('total'))['total_sales'] or 0

    return total_sales_current_year

def get_sales_by_month(request):
    month = request.GET.get('month')
    loja = request.user.loja
    vendas = Pedido.objects.filter(loja=loja, data__month=month).values('data__day').annotate(total_dia=Sum('total'))
    dias = list(vendas.values_list('data__day', flat=True))
    totais = list(vendas.values_list('total_dia', flat=True))
    return JsonResponse({
        'dias': dias,
        'totais': totais
    })


def editar_loja(request):
    loja = request.user.loja
    months, monthly_totals = get_sales_data(request)
    years, annual_totals = get_annual_sales_data(request)
    current_year_sales = get_current_year_sales(request)  # Obtem o total de vendas do ano atual

    context = {
        'months': months,
        'monthly_totals': monthly_totals,
        'years': years,
        'annual_totals': annual_totals,
        'current_year_sales': current_year_sales,  # Passa o total para o contexto
        'loja': loja
    }
    return render(request, 'core/editar_index.html', context)


def editar_loja1(request):
    # Obter o mês selecionado ou usar o mês atual como padrão
    selected_month = request.GET.get('month', now().month)

    loja = request.user.loja

    loja_id = request.user.loja.id

    # Filtra os pedidos no mês e ano selecionado
    sales_data = Pedido.objects.filter(
        loja_id=loja_id,
        data__year=now().year,
        data__month=selected_month
    ).values('data').annotate(total_vendas=Sum('total')).order_by('data')

    sales_dates = [data['data'].strftime('%Y-%m-%d') for data in sales_data]
    sales_totals = [data['total_vendas'] for data in sales_data]
    pedidos_recentes = Pedido.objects.filter(loja=loja, data__month=timezone.now().month).aggregate(Sum('total'))
    total_vendas = pedidos_recentes['total__sum'] if pedidos_recentes['total__sum'] else 0


    context = {
        'sales_dates': sales_dates,
        'sales_totals': sales_totals,
        'selected_month': int(selected_month),
        'total_vendas': total_vendas,
        'pedidos': Pedido.objects.filter(loja=loja).order_by('-data')[:10],  # últimos 10 pedidos
        'loja':loja
    
    }
    return render(request, 'core/editar_index.html', context)


def catalogo(request):
    if not hasattr(request.user, 'loja'):
        return redirect('login')

    loja = request.user.loja

    categoria_form = CategoriaForm()
    produto_form = ProdutoForm()
    produto_editando = None

    # Verificar se estamos editando um produto existente
    produto_id = request.POST.get('produto_id') or request.GET.get('produto_id')
    if produto_id:
                # Editando um produto existente
                produto_editando = get_object_or_404(Produto, id=produto_id, categoria__loja=loja)
                produto_form = ProdutoForm(request.POST, request.FILES, instance=produto_editando)
    else:
        # Criando um novo produto
        produto_form = ProdutoForm(request.POST, request.FILES)
    if request.method == 'POST':
        produto_id = request.POST.get('produto_id')  # Obter o produto_id do formulário
        if 'categoria_submit' in request.POST:
            categoria_form = CategoriaForm(request.POST)
            if categoria_form.is_valid():
                nova_categoria = categoria_form.save(commit=False)
                nova_categoria.loja = loja
                nova_categoria.save()

            else:
                print(categoria_form.errors)


    context = {
        'categoria_form': categoria_form,
        'loja': loja,
    }

    return render(request, 'core/catalogo.html', context)

@login_required
def gerenciar_promocoes(request):
    loja = request.user.loja
    promocoes = Promocao.objects.filter(loja=loja)
    if request.method == 'POST':
        promocao_form = PromocaoForm(request.POST, request.FILES, loja=loja)
        if promocao_form.is_valid():
            nova_promocao = promocao_form.save(commit=False)
            nova_promocao.loja = loja
            nova_promocao.save()
            
            # Atualizar o campo promocao do produto associado
            produto = nova_promocao.produto
            produto.promocao = nova_promocao
            produto.save()

            return redirect('gerenciar_promocoes')
    else:
        promocao_form = PromocaoForm(loja=loja)

    context = {
        'promocao_form': promocao_form,
        'promocoes': promocoes,
        'loja': loja,
    }

    return render(request, 'core/gerenciar_promocoes.html', context)

def remover_produto(request, produto_id):
    if request.method == 'POST':
        produto = get_object_or_404(Produto, id=produto_id)
        produto.delete()
        messages.success(request, 'Produto removido com sucesso.')
        return redirect('catalogo')
    else:
        # Redireciona ou mostra uma mensagem de erro se não for um POST
        messages.error(request, 'Método inválido.')
        return redirect('catalogo')

@login_required
def remover_promocao(request, promocao_id):
    loja = request.user.loja
    promocao = get_object_or_404(Promocao, id=promocao_id, loja=loja)
    
    if request.method == 'POST':
        promocao.delete()
        messages.success(request, 'Promoção removida com sucesso.')
        return redirect('gerenciar_promocoes')
    context = {
        {'promocao': promocao,
        'loja': loja }
    }



def remover_categoria(request, categoria_id):
    if request.method == 'POST':
        categoria = get_object_or_404(CategoriaProduto, id=categoria_id)
        categoria.delete()
        messages.success(request, 'Categoria removida com sucesso.')
        return redirect('catalogo')
    else:
        messages.error(request, 'Método inválido.')
        return redirect('catalogo')

def buscar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    dados = {
        'id': produto.id,
        'nome': produto.nome,
        'preco': produto.preco,
        'descricao': produto.descricao,
        # Inclua outros campos conforme necessário
    }
    return JsonResponse(dados)

def entrega(request):
    loja = request.user.loja
    
    if request.method == 'POST':
        form = LojaForm(request.POST)

        if 'frete' in request.POST and form.is_valid():
            frete = form.cleaned_data['valor_frete']
            loja.valor_frete = frete
            loja.save()
            return redirect('entrega')

            

        elif 'tempo' in request.POST and form.is_valid():
            tempo_min = form.cleaned_data['tempo_entrega_min']
            tempo_max = form.cleaned_data['tempo_entrega_max']

            loja.tempo_entrega_max = tempo_max
            loja.tempo_entrega_min = tempo_min  # Aqui é onde a correção foi feita
            loja.save()
            return redirect('entrega')

        else:
            print(form.errors)

    else:
        form = LojaForm()

    context = {
        'loja': loja,
        'form': form  # Certifique-se de passar o form para o contexto
    }

    return render(request, 'core/entrega.html', context)


def update_capa(request):
    if request.method == 'POST' and 'capa' in request.FILES:
        loja = request.user.loja  # Obtenha o objeto Loja corretamente
        loja.capa = request.FILES['capa']
        loja.save()
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})

def update_foto(request):
    if request.method == 'POST' and 'foto' in request.FILES:
        loja = request.user.loja
        loja.foto = request.FILES['foto']
        loja.save()
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})

def editar_geral(request):
    loja = request.user.loja
    
    if request.method == 'POST':
        form = LojaInfoForm(request.POST, instance=loja)
        if form.is_valid():
            form.save()
            messages.success(request, 'Informações da loja atualizadas com sucesso!')
            return redirect('editar_geral')
        else:
            messages.error(request, 'Corrija os erros abaixo.')
    else:
        form = LojaInfoForm(instance=loja)
    
    context = {
        'loja': loja,
        'form': form
    }
    
    return render(request, 'core/editar_geral.html', context)


def criar_produto(request):
    if not hasattr(request.user, 'loja'):
        return redirect('login')

    loja = request.user.loja
    produto_form = ProdutoForm()
    categoria_form = CategoriaForm()  # Adiciona o formulário de categoria

    if request.method == 'POST':
        if 'produto_submit' in request.POST:
            produto_form = ProdutoForm(request.POST, request.FILES)
            if produto_form.is_valid():
                novo_produto = produto_form.save(commit=False)
                categoria_id = request.POST.get('categoriaId')
                novo_produto.categoria = CategoriaProduto.objects.get(id=categoria_id)
                novo_produto.save()

                opcaoIndex = 0
                while True:
                    opcao_nome = request.POST.get(f'nome_opcao_{opcaoIndex}')
                    if not opcao_nome:
                        break

                    opcao_data = {
                        'nome': opcao_nome,
                        'descricao': request.POST.get(f'descricao_opcao_{opcaoIndex}'),
                        'foto': request.FILES.get(f'foto_opcao_{opcaoIndex}')
                    }
                    opcao_form = OpcaoForm(opcao_data)
                    if opcao_form.is_valid():
                        nova_opcao = opcao_form.save(commit=False)
                        nova_opcao.produto = novo_produto
                        nova_opcao.save()
                    opcaoIndex += 1

                return redirect('catalogo')

            else:
                print(produto_form.errors)

        elif 'categoria_submit' in request.POST:
            categoria_form = CategoriaForm(request.POST)
            if categoria_form.is_valid():
                nova_categoria = categoria_form.save(commit=False)
                nova_categoria.loja = loja
                nova_categoria.save()
                return redirect('catalogo')  # Redireciona após salvar a categoria
            else:
                print(categoria_form.errors)

    context = {
        'produto_form': produto_form,
        'categoria_form': categoria_form,  # Adiciona o formulário de categoria no contexto
        'loja': loja
    }
    return render(request, 'core/catalogo.html', context)

# View para editar um produto existente
def editar_produto(request, produto_id):
    if not hasattr(request.user, 'loja'):
        return redirect('login')

    loja = request.user.loja
    produto_editando = get_object_or_404(Produto, id=produto_id, categoria__loja=loja)
    produto_form = ProdutoForm(instance=produto_editando)

    if request.method == 'POST':
        produto_form = ProdutoForm(request.POST, request.FILES, instance=produto_editando)
        if produto_form.is_valid():
            produto_form.save()
            opcaoIndex = 0
            while True:
                opcao_nome = request.POST.get(f'nome_opcao_{opcaoIndex}')
                if not opcao_nome:
                    break

                opcao_data = {
                    'nome': opcao_nome,
                    'descricao': request.POST.get(f'descricao_opcao_{opcaoIndex}')
                }
                opcao_form = OpcaoForm(opcao_data, {'foto': request.FILES.get(f'foto_opcao_{opcaoIndex}')})
                if opcao_form.is_valid():
                    nova_opcao = opcao_form.save(commit=False)
                    nova_opcao.produto = novo_produto
                    nova_opcao.save()

                opcaoIndex += 1
                return redirect('catalogo')
        else:
            print(produto_form.errors)

    context = {'produto_form': produto_form, 'loja': loja}
    return render(request, 'core/catalogo.html', context)


def criar_subperfil(request):
    if request.method == 'POST':
        form = SubperfilForm(request.POST, request.FILES)
        if form.is_valid():

            subperfil.nome = form.cleaned_data['nome']
            subperfil.foto = form.cleaned_data['foto'] 
            subperfil.titular = request.user.cliente  # Assumindo que o cliente está relacionado ao User
            subperfil.save()
            return redirect('perfil_familia')  # Redirecionar conforme necessário
    else:
        form = SubperfilForm()
    return render(request, 'core/criarSubperfil.html', {'form': form})

@login_required
def perfil_usuario(request):
    cliente = request.user.cliente

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=cliente)
        password_form = PasswordConfirmationForm(request.POST, user=request.user)

        if user_form.is_valid() and password_form.is_valid():
            user_form.save()
            messages.success(request, 'Seu perfil foi atualizado com sucesso!')
            return redirect('perfil_usuario')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        user_form = UserProfileForm(instance=cliente)
        password_form = PasswordConfirmationForm(user=request.user)

    context = {
        'cliente': cliente,
        'user_form': user_form,
        'password_form': password_form,
    }
    
    return render(request, 'core/perfil_usuario.html', context)

def ver_pedidos_loja(request):
    loja = request.user.loja  # Supõe que cada usuário autenticado tem uma loja associada
    pedidos = Pedido.objects.filter(loja=loja).order_by('-data')
    context = {
        'pedidos': pedidos,
        'loja': loja
        }
    return render(request, 'core/pedidos_loja.html', context)


logger = logging.getLogger(__name__)


def marcar_como_entregue(request):
    try:
        loja = request.user.loja
    except: 
        loja = None
        return redirect('home')
    pedidos = Pedido.objects.filter(loja=loja).order_by('-data')
    pedido_id = request.POST.get('pedido_id')
    codigo_secreto = request.POST.get('codigo_secreto')
    
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id, loja=request.user.loja)

        if pedido.status == 'confirmado' and pedido.codigo_secreto == codigo_secreto:
            pedido.status = 'entregue'
            pedido.save()
            messages.success(request, "Pedido marcado como entregue com sucesso.")
        else:
            messages.error(request, "Código secreto incorreto ou pedido não pode ser marcado como entregue.")

    context = {
        'loja': loja,
        'pedidos': pedidos,
        'tokens': {pedido.id: TokenPedido.objects.filter(pedido=pedido, tipo='aceite', expiracao__gt=timezone.now()).first() for pedido in pedidos}
    }
    return render(request, 'core/confirmar_entrega.html', context)
def criar_pedido_loja(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        total = Decimal(request.POST.get('total'))
        descricao = request.POST.get('descricao')
        metodo_pagamento = request.POST.get('pagamento')

        try:
            cliente = CustomUser.objects.get(username=username).cliente
        except CustomUser.DoesNotExist:
            messages.error(request, "Usuário não encontrado.")
            return redirect('criar_pedido_loja')

        if metodo_pagamento == 'pontos' and cliente.pontos < total:
            messages.error(request, "Pontos insuficientes.")
            return redirect('criar_pedido_loja')

        pedido = Pedido.objects.create(
            cliente=cliente,
            loja=request.user.loja,
            total=total,
            descricao=descricao,
            pagamento=metodo_pagamento,
            status='entregue',
            localizacao='Na loja'
        )

        if metodo_pagamento == 'pontos':
            cliente.pontos -= total  # Desconta os pontos
        # Adiciona pontos baseado em 0.4 do total gasto em reais
        cliente.pontos += total * Decimal('0.4')
        cliente.save()

        messages.success(request, "Pedido criado com sucesso.")
        return redirect('criar_pedido_loja')

    context = {
        'loja': request.user.loja
    }
    return render(request, 'core/criar_pedido.html', context)



def strip_tags(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    text_content = soup.get_text()
    return text_content

def distribuir_pontos(request):
    if not hasattr(request.user, 'loja'):
        messages.error(request, 'Apenas lojas podem distribuir pontos.')
        return redirect('home')

    loja = request.user.loja
    funcionarios = loja.funcionarios.filter(lojafuncionario__aceitou_convite=True)

    if request.method == 'POST':
        if 'distribuir_pontos' in request.POST:
            form = DistribuirPontosForm(request.POST, loja=loja)
            if form.is_valid():
                pontos = form.cleaned_data['pontos']
                funcionario = form.cleaned_data['funcionario']
                if pontos > loja.pontos:
                    messages.error(request, 'Pontos insuficientes.')
                else:
                    loja.pontos -= pontos
                    loja.save()
                    funcionario.pontos += pontos
                    funcionario.save()
                    messages.success(request, f'{pontos} pontos foram atribuídos a {funcionario.username}.')
                    return redirect('distribuir_pontos')
        elif 'adicionar_funcionario' in request.POST:
            add_form = AdicionarFuncionarioForm(request.POST)
            if add_form.is_valid():
                cpf = add_form.cleaned_data['cpf']
                funcionario = get_object_or_404(Cliente, username=cpf)
                lojafunc = LojaFuncionario.objects.create(loja=loja, funcionario=funcionario)
                enviar_email_convite_funcionario(request, loja, funcionario, lojafunc.id)
                messages.success(request, f'Convite enviado para {funcionario.username}.')
                return redirect('distribuir_pontos')
    else:
        form = DistribuirPontosForm(loja=loja)
        add_form = AdicionarFuncionarioForm()

    return render(request, 'core/distribuir_pontos.html', {
        'form': form,
        'add_form': add_form,
        'funcionarios': funcionarios,
        'pontos_disponiveis': loja.pontos,
        'loja': loja
    })
def enviar_email_distribuicao_pontos(loja, funcionario, pontos):
    subject = 'Distribuição de Pontos'
    context = {
        'loja': loja,
        'funcionario': funcionario,
        'pontos': pontos
    }
    html_content = render_to_string('core/email_distribuicao_pontos.html', context)
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(subject, text_content, 'seu_email@example.com', [funcionario.email])
    email.attach_alternative(html_content, "text/html")
    email.send()

def enviar_email_convite_funcionario(request, loja, funcionario, lojafunc_id):
    accept_url = reverse('aceitar_convite', args=[lojafunc_id])
    full_accept_url = f'{request.scheme}://{request.get_host()}{accept_url}'
    subject = 'Convite para ser Funcionário'
    context = {
        'loja': loja,
        'funcionario': funcionario,
        'accept_url': full_accept_url
    }
    html_content = render_to_string('core/email_convite_funcionario.html', context)
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(subject, text_content, 'seu_email@example.com', [funcionario.email])
    email.attach_alternative(html_content, "text/html")
    email.send()

def aceitar_convite(request, lojafunc_id):
    lojafunc = get_object_or_404(LojaFuncionario, id=lojafunc_id)
    lojafunc.aceitou_convite = True
    lojafunc.save()
    messages.success(request, 'Convite aceito com sucesso!')
    return redirect('home')