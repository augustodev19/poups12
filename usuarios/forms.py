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
        fields = ['produto', 'quantidade_necessaria', 'ativo', 'imagem', 'descricao']  # Inclua 'descricao'
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-control'}),
            'quantidade_necessaria': forms.NumberInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control'}),  # Widget para 'descricao'
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


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'email', 'foto']

class PasswordConfirmationForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PasswordConfirmationForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise forms.ValidationError("Senha incorreta")
        return password

class SubperfilForm(forms.ModelForm):
    class Meta:
        model = Subperfil
        fields = ['nome', 'foto_perfil']

class LojaInfoForm(forms.ModelForm):
    categorias = forms.ModelMultipleChoiceField(
        queryset=Categoria.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = Loja
        fields = ['nomeLoja', 'nome', 'email', 'categorias']
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model
User = get_user_model()

class EmailPasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        """ Retorna um conjunto de usuários correspondentes para redefinição de senha. """
        # Busca usuários pelo e-mail, independente do estado 'is_active'
        active_users = User._default_manager.filter(email__iexact=email)
        return (u for u in active_users if u.has_usable_password())

class AdicionarFuncionarioForm(forms.Form):
    cpf = forms.CharField( label='CPF do Funcionário')

class DistribuirPontosForm(forms.ModelForm):
    pontos = forms.DecimalField(max_digits=10, decimal_places=2, label='Pontos')

    class Meta:
        model = LojaFuncionario
        fields = ['funcionario', 'pontos']

    def __init__(self, *args, **kwargs):
        loja = kwargs.pop('loja', None)
        super(DistribuirPontosForm, self).__init__(*args, **kwargs)
        if loja:
            self.fields['funcionario'].queryset = loja.funcionarios.filter(lojafuncionario__aceitou_convite=True)