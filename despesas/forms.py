from calendar import monthrange
from datetime import date

from django import forms
from django.utils import timezone

from cadastros.models import SubcategoriaDeSpesa

from .models import Despesa
from .services import expense_period_choices


class DateInput(forms.DateInput):
    input_type = "date"


MONTH_CHOICES = [
    (1, "Janeiro"),
    (2, "Fevereiro"),
    (3, "Março"),
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

RECORRENCIA_TIPO_CHOICES = [
    ("", "Sem definicao"),
    ("data", "Data final"),
    ("quantidade", "Quantidade de repeticoes"),
]


class DespesaForm(forms.ModelForm):
    recorrente = forms.BooleanField(
        label="Criar recorrencia mensal",
        required=False,
        help_text="Use para contas que se repetem todo mes.",
    )
    recorrencia_ativa = forms.BooleanField(
        label="Recorrencia ativa",
        required=False,
        initial=True,
        help_text="Desative para parar de gerar proximos lancamentos.",
    )
    recorrencia_data_fim = forms.DateField(
        label="Data final da recorrencia",
        required=False,
        widget=DateInput(),
        help_text="Opcional. Se preenchido, a recorrencia para neste mes.",
    )
    recorrencia_tipo_fim = forms.ChoiceField(
        label="Como definir o encerramento",
        required=False,
        choices=RECORRENCIA_TIPO_CHOICES,
        help_text="Escolha entre informar uma data final ou a quantidade de repeticoes.",
    )
    recorrencia_quantidade = forms.IntegerField(
        label="Quantidade de repeticoes",
        required=False,
        min_value=1,
        help_text="Informe quantas vezes a despesa deve se repetir, incluindo este lancamento.",
    )

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
            "recorrente",
            "recorrencia_ativa",
            "recorrencia_tipo_fim",
            "recorrencia_data_fim",
            "recorrencia_quantidade",
        ]
        widgets = {"data_vencimento": DateInput(), "data_pagamento": DateInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.localdate()
        has_existing_recurrence = bool(self.instance.pk and self.instance.recorrencia)

        year_choices = sorted(
            {today.year - 1, today.year, today.year + 1}
            | {int(periodo.split("-")[0]) for periodo, _ in expense_period_choices()}
        )
        self.fields["mes_referencia"].widget = forms.Select(choices=MONTH_CHOICES)
        self.fields["ano_referencia"].widget = forms.Select(choices=[(year, str(year)) for year in year_choices])

        if not self.instance.pk:
            self.fields["mes_referencia"].initial = today.month
            self.fields["ano_referencia"].initial = today.year

        categoria_id = self.data.get("categoria") or getattr(self.instance, "categoria_id", None)
        if categoria_id:
            self.fields["subcategoria"].queryset = SubcategoriaDeSpesa.objects.filter(categoria_id=categoria_id).order_by("nome")
        else:
            self.fields["subcategoria"].queryset = SubcategoriaDeSpesa.objects.none()

        self.fields["descricao"].widget.attrs.update({"placeholder": "Ex.: aluguel da unidade, energia, contador"})
        self.fields["valor"].widget.attrs.update({"placeholder": "0,00", "inputmode": "decimal"})
        self.fields["data_vencimento"].widget.attrs.update({"placeholder": "Selecione o vencimento"})
        self.fields["data_pagamento"].widget.attrs.update({"placeholder": "Selecione o pagamento"})
        self.fields["observacao"].widget.attrs.update({"placeholder": "Adicione contexto, centro de custo ou observacoes internas...", "rows": 4})
        self.fields["recorrencia_quantidade"].widget.attrs.update({"placeholder": "Ex.: 12"})
        self.fields["pago"].widget.attrs.update({"class": "form-check-input"})

        if has_existing_recurrence:
            self.fields["recorrente"].initial = True
            self.fields["recorrencia_ativa"].initial = self.instance.recorrencia.ativa
            self.fields["recorrencia_data_fim"].initial = self.instance.recorrencia.data_fim
            if self.instance.recorrencia.data_fim:
                inicio = self.instance.recorrencia.data_inicio
                fim = self.instance.recorrencia.data_fim
                self.fields["recorrencia_quantidade"].initial = ((fim.year - inicio.year) * 12) + (fim.month - inicio.month) + 1
                self.fields["recorrencia_tipo_fim"].initial = "data"
        else:
            self.fields.pop("recorrencia_ativa")

        submitted_tipo = self.data.get("recorrencia_tipo_fim")
        if submitted_tipo in {"data", "quantidade"}:
            self.fields["recorrencia_tipo_fim"].initial = submitted_tipo

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("recorrente"):
            cleaned_data["recorrencia_tipo_fim"] = ""
            cleaned_data["recorrencia_data_fim"] = None
            cleaned_data["recorrencia_quantidade"] = None
            return cleaned_data

        tipo_fim = cleaned_data.get("recorrencia_tipo_fim")
        fim = cleaned_data.get("recorrencia_data_fim")
        quantidade = cleaned_data.get("recorrencia_quantidade")
        inicio = date(
            int(cleaned_data.get("ano_referencia") or 1),
            int(cleaned_data.get("mes_referencia") or 1),
            1,
        )

        if tipo_fim == "data":
            cleaned_data["recorrencia_quantidade"] = None
            if not fim:
                self.add_error("recorrencia_data_fim", "Informe a data final da recorrencia.")
                return cleaned_data
            if fim < inicio:
                self.add_error("recorrencia_data_fim", "A data de termino nao pode ser anterior ao mes de referencia.")
            return cleaned_data

        if tipo_fim == "quantidade":
            cleaned_data["recorrencia_data_fim"] = None
            if not quantidade:
                self.add_error("recorrencia_quantidade", "Informe a quantidade de repeticoes.")
                return cleaned_data
            if quantidade < 1:
                self.add_error("recorrencia_quantidade", "A quantidade deve ser maior que zero.")
                return cleaned_data
            cleaned_data["recorrencia_data_fim"] = None
            total_meses = quantidade - 1
            fim_year = inicio.year + ((inicio.month - 1 + total_meses) // 12)
            fim_month = ((inicio.month - 1 + total_meses) % 12) + 1
            fim_day = monthrange(fim_year, fim_month)[1]
            cleaned_data["recorrencia_data_fim"] = date(fim_year, fim_month, fim_day)
            return cleaned_data

        cleaned_data["recorrencia_data_fim"] = None
        cleaned_data["recorrencia_quantidade"] = None
        return cleaned_data
