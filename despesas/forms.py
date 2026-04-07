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
        label="Termino da recorrencia",
        required=False,
        widget=DateInput(),
        help_text="Opcional. Se preenchido, a recorrencia para neste mes.",
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
            "recorrencia_data_fim",
        ]
        widgets = {"data_vencimento": DateInput(), "data_pagamento": DateInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.localdate()

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

        if self.instance.pk and self.instance.recorrencia:
            self.fields["recorrente"].initial = True
            self.fields["recorrencia_ativa"].initial = self.instance.recorrencia.ativa
            self.fields["recorrencia_data_fim"].initial = self.instance.recorrencia.data_fim

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("recorrente") and cleaned_data.get("recorrencia_data_fim"):
            fim = cleaned_data["recorrencia_data_fim"]
            inicio = date(
                int(cleaned_data.get("ano_referencia") or 1),
                int(cleaned_data.get("mes_referencia") or 1),
                1,
            )
            if fim < inicio:
                self.add_error("recorrencia_data_fim", "A data de termino nao pode ser anterior ao mes de referencia.")
        return cleaned_data
