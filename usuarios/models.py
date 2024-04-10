from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from datetime import datetime
import logging
from django.utils import timezone
import stripe
from django.utils.timezone import timedelta
from django.utils.translation import gettext_lazy as _
import uuid
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

class Endereco(models.Model):
    rua = models.CharField(max_length=255)
    numero = models.IntegerField(null=True, blank=True)
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
    foto = models.ImageField(upload_to='images/', blank=True, null=True, default="/images/unknown.png")


    def __str__(self):
        return self.nome


class Loja(CustomUser):
    nomeLoja = models.CharField(max_length=100, blank=True)
    capa = models.ImageField(upload_to='images/', blank=True, null=True, default="/images/unknown.png")
    foto = models.ImageField(upload_to='images/', blank=True, null=True, default="/images/unknown.png")
    categorias = models.ManyToManyField(Categoria, related_name='lojas', blank=True)
    endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE, blank=True, null=True)
    valor_frete = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default="0")
    frete_gratis = models.BooleanField(default=False)
    vale_refeicao = models.ManyToManyField(ValeRefeicao, related_name='vale_refeicao', blank=True)
    tempo_entrega = models.IntegerField(blank=True, null=True)
    token_pagseguro = models.CharField(max_length=100, blank=True, null=True)
    email_pagseguro = models.CharField(max_length=100, blank=True, null=True)
    saldo = models.DecimalField(max_digits = 99999999999, decimal_places=2, blank=True, null=True, default="0")
    ever_saldo = models.DecimalField(max_digits = 99999999999, decimal_places=2, blank=True, null=True, default="0")
    is_active = models.BooleanField(default=True)
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
    foto = models.ImageField(upload_to='images/', blank=True, null=True, default="/images/unknown.png")
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
    foto = models.ImageField(upload_to='images/', blank=True, null=True, default="/images/unknown.png")
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.CharField(max_length=1000, blank=True, null=True)
    pontos = models.IntegerField(default=0)

    # outros campos do produto

    def __str__(self):
        return self.nome
            # outros campos da loja

class Opcao(models.Model):
    foto = models.ImageField(upload_to='images/', blank=True, null=True, default="/images/unknown.png")
    produto = models.ForeignKey(Produto, related_name='opcoes', on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    descricao = models.CharField(max_length=1000, blank=True, null=True)

    # outros campos das opções do produto

    def __str__(self):
        return f"{self.nome} - {self.produto.nome}"

class ItemOpcao(models.Model):
    foto = models.ImageField(upload_to='images/', blank=True, null=True, default="/images/unknown.png")
    opcao = models.ForeignKey(Opcao, related_name='itens', on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    preco_adicional = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    descricao = models.CharField(max_length=1000, blank=True, null=True)


    def __str__(self):
        return f"{self.nome} - {self.opcao.nome}"


class Cliente(CustomUser):
    foto = models.ImageField(upload_to='images/', blank=True, null=True)
    endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE, blank=True, null=True)
    saldo_poups = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pontos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    plano_familia = models.BooleanField(default=False, verbose_name=_('Plano Família'))




class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, blank=True, null=True)
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, blank=True, null=True)
    categoria = models.ForeignKey(CategoriaProduto, on_delete=models.CASCADE, blank=True, null=True)
    foto = models.ImageField(upload_to='images/', blank=True, null=True, default="/images/unknown.png")
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.CharField(max_length=1000, blank=True, null=True)
    pontos = models.IntegerField(default=0)

    # outros campos do produto

    def __str__(self):
        return self.nome
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
    foto_perfil = models.ImageField(upload_to='subclientes_fotos/', blank=True, null=True)

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if self.titular.subperfis.count() >= 4:
            raise ValidationError('Não é possível adicionar mais de 4 subperfis para um titular.')
        super(Subperfil, self).save(*args, **kwargs)

