from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import stripe
from django.utils.timezone import timedelta
from django.utils.translation import gettext_lazy as _
import uuid
from decimal import Decimal
from django.dispatch import receiver
from django.db.models.signals import post_save

from poupsapp import settings
from django import forms
from PIL import Image
import requests
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType



class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('O campo email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)




class CustomUser(AbstractBaseUser, PermissionsMixin):
    nome = models.CharField(_('nome'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('CPF ou CNPJ'), max_length=30, unique=True)
    telefone = models.CharField(_('telefone'), max_length=20, blank=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    is_staff = models.BooleanField(_('staff status'), default=False)


    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_name="customuser_groups",
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="customuser_user_permissions",
        related_query_name="customuser",
    )




class Estado(models.Model):
    nome = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nome

class Cidade(models.Model):
    estado = models.ForeignKey(Estado, related_name='cidades', on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nome



class Bairro(models.Model):
    nome = models.CharField(max_length=255)
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome


class CEP(models.Model):
    codigo = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.codigo

def default_expiration_date():
    return timezone.now() + timedelta(days=1)


class TokenPedido(models.Model):
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE)
    token = models.CharField(max_length=64)
    tipo = models.CharField(max_length=10)  # 'aceite' ou 'recusa'
    expiracao = models.DateTimeField(default=default_expiration_date)

    def __str__(self):
        return f"{self.tipo} token para pedido {self.pedido.id} expira em {self.expiracao}"

class Endereco(models.Model):
    rua = models.CharField(max_length=255)
    numero = models.CharField(max_length=50, null=True, blank=True)
    complemento = models.CharField(max_length=50, null=True, blank=True)
    bairro = models.ForeignKey(Bairro, on_delete=models.CASCADE)
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    cep = models.ForeignKey(CEP, on_delete=models.CASCADE)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.rua

class ValeRefeicao(models.Model):
    nome = models.CharField(max_length=50, blank=True, null=True)
    foto = models.ImageField( upload_to='images/', blank=True, null=True, max_length=None)


class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='images/', blank=True, null=True, default="/images/ella-olsson-oPBjWBCcAEo-unsplash_1.jpg")


    def __str__(self):
        return self.nome

class Cliente(CustomUser):
    foto = models.ImageField(upload_to='images/', blank=True, null=True, default='images/user_2.png')
    endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE, blank=True, null=True)
    saldo_poups = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pontos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    plano_familia = models.BooleanField(default=False, verbose_name=_('Plano Família'))



class Loja(CustomUser):
    nomeLoja = models.CharField(max_length=100, blank=True)
    capa = models.ImageField(upload_to='images/', blank=True, null=True, default="/images/ella-olsson-oPBjWBCcAEo-unsplash_1.jpg")
    foto = models.ImageField(upload_to='images/', blank=True, null=True, default="/images/ella-olsson-oPBjWBCcAEo-unsplash_1.jpg")
    categorias = models.ManyToManyField(Categoria, related_name='lojas', blank=True)
    endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE, blank=True, null=True)
    valor_frete = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default="0")
    frete_gratis = models.BooleanField(default=False)
    vale_refeicao = models.ManyToManyField(ValeRefeicao, related_name='vale_refeicao', blank=True)
    tempo_entrega = models.IntegerField(blank=True, null=True)
    stripe_payout_id = models.CharField(max_length=255, null=True, blank=True)
    tempo_entrega_min = models.IntegerField(blank=True, null=True, default=65)
    tempo_entrega_max = models.IntegerField(blank=True, null=True, default=75)
    token_pagseguro = models.CharField(max_length=100, blank=True, null=True)
    email_pagseguro = models.CharField(max_length=100, blank=True, null=True)
    saldo = models.DecimalField(max_digits = 20, decimal_places=2, blank=True, null=True, default="0")
    ever_saldo = models.DecimalField(max_digits = 20, decimal_places=2, blank=True, null=True, default="0")
    is_active = models.BooleanField(default=True)
    pontos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    funcionarios = models.ManyToManyField(Cliente, through='LojaFuncionario', related_name='empresas')
      # campo adicionado
    def delete(self, *args, **kwargs):
        """
        Sobrescreve o método delete para implementar soft delete.
        Em vez de deletar a loja, marca-a como inativa.
        """
        self.is_active = False
        self.save()

    def __str__(self):
        return self.nome





class CategoriaProduto(models.Model):
    foto = models.ImageField(upload_to='images/', blank=True, null=True, default="/images/ella-olsson-oPBjWBCcAEo-unsplash_1.jpg")
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, blank=True, null=True)
    nome = models.CharField(max_length=100, blank=True, null=True)
    descricao = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        # Retorna self.nome se ele existir e não for uma string vazia.
        # Caso contrário, retorna uma string padrão como 'Produto sem nome'.
        return self.nome if self.nome else 'Produto sem nome'


    

class Produto(models.Model):
    pontos = models.IntegerField(blank=True, null=True)
    categoria = models.ForeignKey(CategoriaProduto, on_delete=models.CASCADE, blank=True, null=True)
    foto = models.ImageField(upload_to='images/', blank=True, null=True, default="/images/ella-olsson-oPBjWBCcAEo-unsplash_1.jpg")
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.CharField(max_length=1000, blank=True, null=True)
    pontos = models.IntegerField(default=0)
    promocao = models.ForeignKey('Promocao', on_delete=models.SET_NULL, null=True, blank=True, related_name='produtos')

    # outros campos do produto
    def save(self, *args, **kwargs):
        if self.preco is not None:
            # Convertendo 0.4 para Decimal antes da multiplicação
            pontos_decimal = Decimal('0.4')  
            self.pontos = int(self.preco * pontos_decimal)
        super(Produto, self).save(*args, **kwargs)

    def __str__(self):
        return self.nome
            # outros campos da loja

class Opcao(models.Model):
    foto = models.ImageField(upload_to='images/', blank=True, null=True, default="/images/ella-olsson-oPBjWBCcAEo-unsplash_1.jpg")
    produto = models.ForeignKey(Produto, related_name='opcoes', on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    descricao = models.CharField(max_length=1000, blank=True, null=True)

    # outros campos das opções do produto

    def __str__(self):
        return f"{self.nome} - {self.produto.nome}"

class ItemOpcao(models.Model):
    foto = models.ImageField(upload_to='images/', blank=True, null=True, default="/images/ella-olsson-oPBjWBCcAEo-unsplash_1.jpg")
    opcao = models.ForeignKey(Opcao, related_name='itens', on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    preco_adicional = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    descricao = models.CharField(max_length=1000, blank=True, null=True)


    def __str__(self):
        return f"{self.nome} - {self.opcao.nome}"









class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, blank=True, null=True)
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, blank=True, null=True)
    nome = models.CharField(max_length=100)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    descricao = models.CharField(max_length=1000, blank=True, null=True)
    pontos = models.IntegerField(default=0)
    data = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    localizacao = models.CharField(blank=True, null=True, max_length=400)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, default='none')  # Alterado de confirmado para estado
    pagamento = models.CharField(max_length=50, default='none')
    retirada_na_loja = models.BooleanField(default=False, blank=True, null=True)
    correlation_id = models.CharField(max_length=200, null=True, blank=True)
    codigo_secreto = models.CharField(max_length=200, null=True, blank=True)


    

class ItemPedido(models.Model):
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE)
    produto = models.ForeignKey('Produto', on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    imagem_url = models.URLField(null=True, blank=True)  # Campo opcional para a URL da imagem

    def subtotal(self):
        return self.quantidade * self.preco_unitario  # outros campos do produto
            # outros campos da loja

class CarrinhoItem(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1)
    adicionado_em = models.DateTimeField(auto_now_add=True)

class Carrinho(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    itens = models.ManyToManyField(CarrinhoItem)
    criado_em = models.DateTimeField(auto_now_add=True)


class Subperfil(models.Model):
    titular = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='subperfis')
    nome = models.CharField(max_length=100)
    foto_perfil = models.ImageField(upload_to='subclientes_fotos/', blank=True, null=True, default='images/user_2.png')
    is_titular = models.BooleanField(default=False)

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.pk and self.titular.subperfis.count() >= 4:
            raise ValidationError('Não é possível adicionar mais de 4 subperfis para um titular.')
        super(Subperfil, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.is_titular:
            raise ValidationError('O subperfil do titular não pode ser excluído.')
        super(Subperfil, self).delete(*args, **kwargs)


@receiver(post_save, sender=Cliente)
def create_subperfil_titular(sender, instance, created, **kwargs):
    if created and instance.plano_familia:
        Subperfil.objects.create(titular=instance, nome=instance.nome, is_titular=True)


class Promocao(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='promocoes')
    quantidade_necessaria = models.PositiveIntegerField()
    imagem = models.ImageField(upload_to='images/', blank=True, null=True, default="/images/ella-olsson-oPBjWBCcAEo-unsplash_1.jpg")
    ativo = models.BooleanField(default=True)
    descricao = models.CharField(max_length=250, null=True, blank=True)
    def __str__(self):
        return f"{self.produto.nome} - Compre {self.quantidade_necessaria}, Ganhe 1"

class CompraAcumulada(models.Model):
    promocao = models.ForeignKey(Promocao, on_delete=models.CASCADE, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade_comprada = models.PositiveIntegerField(default=0)
    pontos_para_proxima_promocao = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.cliente.nome} - {self.produto.nome}: {self.quantidade_comprada}"

    def quantidade_promocoes(self):
        if self.promocao:
            return self.quantidade_comprada // self.promocao.quantidade_necessaria
        return 0



class Charge(models.Model):
    charge_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    endereco = models.CharField(max_length=255, null=True, blank=True)
    loja_id = models.IntegerField()
    cliente_id = models.IntegerField()
    correlation_id = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    attempts = models.IntegerField(default=0)  # Número de tentativas de verificação
    last_error = models.TextField(null=True, blank=True)
    retirada_na_loja = models.BooleanField(default=False, blank=True, null=True)  # Última mensagem de erro
    payment_status = models.CharField(max_length=20, default='pending')  # Novo campo para rastrear o status do pagamento
    def __str__(self):
        return self.charge_id


class LojaFuncionario(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    funcionario = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    aceitou_convite = models.BooleanField(default=False)

    class Meta:
        unique_together = ('loja', 'funcionario')  # Garante a unicidade

    def __str__(self):
        return f"{self.loja.nomeLoja} - {self.funcionario.username}"