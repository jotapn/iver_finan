from django import forms

from .models import Banco, Cargo, CategoriaDeSpesa, Colaborador, FormaPagamento, Setor, SubcategoriaDeSpesa


class DateInput(forms.DateInput):
    input_type = "date"


class BancoForm(forms.ModelForm):
    class Meta:
        model = Banco
        fields = ["nome"]


class SetorForm(forms.ModelForm):
    class Meta:
        model = Setor
        fields = ["nome"]


class CargoForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = ["nome", "setor", "comissao_percentual"]


class ColaboradorForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = ["nome", "cargo", "ativo", "data_admissao", "data_demissao"]
        widgets = {"data_admissao": DateInput(), "data_demissao": DateInput()}


class FormaPagamentoForm(forms.ModelForm):
    class Meta:
        model = FormaPagamento
        fields = ["nome"]


class CategoriaDeSpesaForm(forms.ModelForm):
    class Meta:
        model = CategoriaDeSpesa
        fields = ["nome"]


class SubcategoriaDeSpesaForm(forms.ModelForm):
    class Meta:
        model = SubcategoriaDeSpesa
        fields = ["nome", "categoria"]
