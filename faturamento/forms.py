from django import forms

from .models import RegistroFaturamento


class DateInput(forms.DateInput):
    input_type = "date"


class RegistroFaturamentoForm(forms.ModelForm):
    class Meta:
        model = RegistroFaturamento
        fields = [
            "data",
            "valor_dinheiro",
            "valor_pix",
            "valor_credito",
            "valor_debito",
            "valor_fiado",
            "valor_vale",
            "faturamento_bar",
            "faturamento_cozinha",
            "observacao",
        ]
        widgets = {"data": DateInput()}
