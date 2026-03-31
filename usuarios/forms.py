from django import forms
from django.contrib.auth import get_user_model

from .models import Perfil, PerfilAcesso

User = get_user_model()


class UsuarioCreateForm(forms.ModelForm):
    password1 = forms.CharField(label="senha", widget=forms.PasswordInput)
    password2 = forms.CharField(label="confirmar senha", widget=forms.PasswordInput)
    perfil_acesso = forms.ModelChoiceField(label="perfil de acesso", queryset=PerfilAcesso.objects.order_by("nome"), required=False)
    nome_completo = forms.CharField(label="nome completo", required=False)
    telefone = forms.CharField(label="telefone", required=False)
    cargo = forms.CharField(label="cargo", required=False)
    observacao = forms.CharField(label="observacao", required=False, widget=forms.Textarea(attrs={"rows": 3}))

    class Meta:
        model = User
        fields = ["username", "email", "is_active"]
        labels = {
            "username": "usuario",
            "email": "email",
            "is_active": "ativo",
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            self.add_error("password2", "As senhas nao coincidem.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email", "")
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            perfil = user.perfil
            perfil.perfil_acesso = self.cleaned_data.get("perfil_acesso")
            perfil.nome_completo = self.cleaned_data.get("nome_completo", "")
            perfil.telefone = self.cleaned_data.get("telefone", "")
            perfil.cargo = self.cleaned_data.get("cargo", "")
            perfil.observacao = self.cleaned_data.get("observacao", "")
            perfil.save()
        return user


class UsuarioUpdateForm(forms.ModelForm):
    nova_senha = forms.CharField(label="nova senha", required=False, widget=forms.PasswordInput)
    confirmar_nova_senha = forms.CharField(label="confirmar nova senha", required=False, widget=forms.PasswordInput)
    perfil_acesso = forms.ModelChoiceField(label="perfil de acesso", queryset=PerfilAcesso.objects.order_by("nome"), required=False)
    nome_completo = forms.CharField(label="nome completo", required=False)
    telefone = forms.CharField(label="telefone", required=False)
    cargo = forms.CharField(label="cargo", required=False)
    observacao = forms.CharField(label="observacao", required=False, widget=forms.Textarea(attrs={"rows": 3}))

    class Meta:
        model = User
        fields = ["username", "email", "is_active"]
        labels = {
            "username": "usuario",
            "email": "email",
            "is_active": "ativo",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        perfil = getattr(self.instance, "perfil", None)
        if perfil:
            self.fields["perfil_acesso"].initial = perfil.perfil_acesso
            self.fields["nome_completo"].initial = perfil.nome_completo
            self.fields["telefone"].initial = perfil.telefone
            self.fields["cargo"].initial = perfil.cargo
            self.fields["observacao"].initial = perfil.observacao

    def clean(self):
        cleaned_data = super().clean()
        nova_senha = cleaned_data.get("nova_senha")
        confirmar = cleaned_data.get("confirmar_nova_senha")
        if nova_senha or confirmar:
            if nova_senha != confirmar:
                self.add_error("confirmar_nova_senha", "As senhas nao coincidem.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        nova_senha = self.cleaned_data.get("nova_senha")
        if nova_senha:
            user.set_password(nova_senha)
        if commit:
            user.save()
            perfil, _ = Perfil.objects.get_or_create(user=user)
            perfil.perfil_acesso = self.cleaned_data.get("perfil_acesso")
            perfil.nome_completo = self.cleaned_data.get("nome_completo", "")
            perfil.telefone = self.cleaned_data.get("telefone", "")
            perfil.cargo = self.cleaned_data.get("cargo", "")
            perfil.observacao = self.cleaned_data.get("observacao", "")
            perfil.save()
        return user


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ["nome_completo", "telefone", "cargo", "observacao"]
        labels = {
            "nome_completo": "nome completo",
            "telefone": "telefone",
            "cargo": "cargo",
            "observacao": "observacao",
        }
        widgets = {"observacao": forms.Textarea(attrs={"rows": 4})}


class PerfilAcessoForm(forms.ModelForm):
    class Meta:
        model = PerfilAcesso
        fields = [
            "nome",
            "ver_dashboard",
            "ver_cadastros",
            "ver_faturamento",
            "ver_despesas",
            "ver_folha",
            "ver_dre",
            "ver_usuarios",
            "ver_admin",
        ]
