from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError

from .models import RegistroFaturamento


class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, **kwargs):
        kwargs.setdefault("format", "%Y-%m-%d")
        super().__init__(**kwargs)


class RegistroFaturamentoForm(forms.ModelForm):
    data = forms.DateField(widget=DateInput(), input_formats=["%Y-%m-%d"])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "quantidade_pessoas": "Ex.: 84",
            "valor_dinheiro": "0,00",
            "valor_pix": "0,00",
            "valor_credito": "0,00",
            "valor_debito": "0,00",
            "valor_fiado": "0,00",
            "valor_vale": "0,00",
            "faturamento_bar": "0,00",
            "faturamento_cozinha": "0,00",
            "faturamento_produtos": "0,00",
            "faturamento_outros": "0,00",
        }
        for field_name, placeholder in placeholders.items():
            self.fields[field_name].widget.attrs.update({"placeholder": placeholder})
        self.fields["observacao"].widget.attrs.update({"placeholder": "Movimento do dia, eventos, anomalias ou observacoes da operacao...", "rows": 4})

    class Meta:
        model = RegistroFaturamento
        fields = [
            "data",
            "quantidade_pessoas",
            "valor_dinheiro",
            "valor_pix",
            "valor_credito",
            "valor_debito",
            "valor_fiado",
            "valor_vale",
            "faturamento_bar",
            "faturamento_cozinha",
            "faturamento_produtos",
            "faturamento_outros",
            "observacao",
        ]
        widgets = {"data": DateInput()}

    def clean(self):
        cleaned_data = super().clean()
        total_pagamentos = sum(
            [
                cleaned_data.get("valor_dinheiro") or Decimal("0.00"),
                cleaned_data.get("valor_pix") or Decimal("0.00"),
                cleaned_data.get("valor_credito") or Decimal("0.00"),
                cleaned_data.get("valor_debito") or Decimal("0.00"),
                cleaned_data.get("valor_fiado") or Decimal("0.00"),
                cleaned_data.get("valor_vale") or Decimal("0.00"),
            ],
            start=Decimal("0.00"),
        )
        total_categorias = sum(
            [
                cleaned_data.get("faturamento_bar") or Decimal("0.00"),
                cleaned_data.get("faturamento_cozinha") or Decimal("0.00"),
                cleaned_data.get("faturamento_produtos") or Decimal("0.00"),
                cleaned_data.get("faturamento_outros") or Decimal("0.00"),
            ],
            start=Decimal("0.00"),
        )

        if total_categorias > total_pagamentos:
            raise ValidationError(
                "A soma de Bar, Cozinha, Produtos e Outros nao pode ser maior que o total do dia informado nos pagamentos."
            )

        return cleaned_data
