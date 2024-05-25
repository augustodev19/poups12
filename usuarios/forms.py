from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import *
from django.forms import ModelForm


class ClienteRegistrationForm(UserCreationForm):
    cep = forms.CharField(max_length=9, required=True)
    image = forms.ImageField(required=False)
    

    class Meta:
        model = Cliente
        fields = ['email', 'password1', 'password2', 'cep', 'nome', 'username', 'telefone', 'foto']


class LojaRegistrationForm(UserCreationForm):
    cep = forms.CharField(max_length=9, required=True)
    image = forms.ImageField(required=False)
    categorias = forms.ModelMultipleChoiceField(
        queryset=Categoria.objects.all(), 
        widget=forms.CheckboxSelectMultiple, 
        required=False
    )
    

    class Meta:
        model = Loja
        fields = ['nomeLoja', 'username', 'foto', 'categorias', 'email', 'telefone', 'nome']

class PromocaoForm(forms.ModelForm):
    class Meta:
        model = Promocao
        fields = ['produto', 'quantidade_necessaria', 'ativo', 'imagem']
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-control'}),
            'quantidade_necessaria': forms.NumberInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        loja = kwargs.pop('loja', None)
        super().__init__(*args, **kwargs)
        if loja:
            self.fields['produto'].queryset = Produto.objects.filter(categoria__loja=loja)


class SubperfilForm(forms.ModelForm):
    class Meta:
        model = Subperfil
        fields = ['nome', 'foto_perfil', 'is_titular']


class LojaForm(ModelForm):
    class Meta:
        model = Loja
        fields = [ 'valor_frete', 'tempo_entrega', 'tempo_entrega_min', 'tempo_entrega_max']


class EditarClienteForm(ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'foto', 'email', 'telefone']

class LoginForm(AuthenticationForm):
    email = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Email ou CPF'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Senha'}))

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = CategoriaProduto
        fields = ['nome', 'descricao', 'foto']

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [ 'nome', 'preco', 'foto', 'descricao']  # Adicione outros campos necessários

class OpcaoForm(forms.ModelForm):
    class Meta:
        model = Opcao
        fields = ['nome', 'descricao', 'foto']  # Removido 'produto', será definido no backend

class ItemOpcaoForm(forms.ModelForm):
    class Meta:
        model = ItemOpcao
        fields = ['nome', 'preco_adicional', 'descricao', 'foto']  # Removido 'opcao', será definido no backend


class SubperfilForm(forms.ModelForm):
    class Meta:
        model = Subperfil
        fields = ['nome', 'foto_perfil']