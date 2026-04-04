from django import forms

from .models import BeneficioColaborador, LancamentoColaborador, PeriodoFolha


MONTH_CHOICES = [
    (1, "Janeiro"),
    (2, "Fevereiro"),
    (3, "Marco"),
    (4, "Abril"),
    (5, "Maio"),
    (6, "Junho"),
    (7, "Julho"),
    (8, "Agosto"),
    (9, "Setembro"),
    (10, "Outubro"),
    (11, "Novembro"),
    (12, "Dezembro"),
]


class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("format", "%Y-%m-%d")
        super().__init__(*args, **kwargs)


class PeriodoFolhaForm(forms.ModelForm):
    mes = forms.TypedChoiceField(choices=MONTH_CHOICES, coerce=int, label="Mes")
    ano = forms.IntegerField(label="Ano", min_value=2000)

    class Meta:
        model = PeriodoFolha
        fields = ["mes", "ano"]


class LancamentoColaboradorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = "form-control"
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {css_class}".strip()
        for field_name in ["consumo_colaborador", "descontos", "produtividade_1_valor", "produtividade_2_valor"]:
            self.fields[field_name].widget.attrs.setdefault("step", "0.01")

    class Meta:
        model = LancamentoColaborador
        fields = [
            "consumo_colaborador",
            "descontos",
            "adiantamento_data",
            "saldo_final_data",
            "produtividade_1_valor",
            "produtividade_1_data",
            "produtividade_2_valor",
            "produtividade_2_data",
        ]
        widgets = {
            "adiantamento_data": DateInput(),
            "saldo_final_data": DateInput(),
            "produtividade_1_data": DateInput(),
            "produtividade_2_data": DateInput(),
        }


class BeneficioColaboradorForm(forms.ModelForm):
    class Meta:
        model = BeneficioColaborador
        fields = ["colaborador", "vale_transporte", "ajuda_custo", "data_vencimento", "data_pagamento", "pago"]
        widgets = {"data_vencimento": DateInput(), "data_pagamento": DateInput()}
