from django import forms

from .models import Despesa


class DateInput(forms.DateInput):
    input_type = "date"


class DespesaForm(forms.ModelForm):
    class Meta:
        model = Despesa
        fields = [
            "descricao",
            "categoria",
            "subcategoria",
            "valor",
            "data_vencimento",
            "data_pagamento",
            "forma_pagamento",
            "banco",
            "pago",
            "mes_referencia",
            "ano_referencia",
            "observacao",
        ]
        widgets = {"data_vencimento": DateInput(), "data_pagamento": DateInput()}
