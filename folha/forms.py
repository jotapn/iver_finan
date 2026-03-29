from django import forms

from .models import BeneficioColaborador, DespesaTrabalhistaMensal, LancamentoColaborador, PeriodoFolha


class DateInput(forms.DateInput):
    input_type = "date"


class PeriodoFolhaForm(forms.ModelForm):
    class Meta:
        model = PeriodoFolha
        fields = ["mes", "ano"]


class LancamentoColaboradorForm(forms.ModelForm):
    class Meta:
        model = LancamentoColaborador
        fields = [
            "salario_bruto",
            "vale_consumo",
            "adicional_noturno",
            "dsr",
            "produtividade_1_valor",
            "produtividade_1_data",
            "produtividade_2_valor",
            "produtividade_2_data",
        ]
        widgets = {"produtividade_1_data": DateInput(), "produtividade_2_data": DateInput()}


class BeneficioColaboradorForm(forms.ModelForm):
    class Meta:
        model = BeneficioColaborador
        fields = ["colaborador", "vale_transporte", "ajuda_custo", "data_vencimento", "data_pagamento", "pago"]
        widgets = {"data_vencimento": DateInput(), "data_pagamento": DateInput()}


class DespesaTrabalhistaMensalForm(forms.ModelForm):
    class Meta:
        model = DespesaTrabalhistaMensal
        fields = ["tipo", "valor", "data_vencimento", "data_pagamento", "banco", "pago"]
        widgets = {"data_vencimento": DateInput(), "data_pagamento": DateInput()}
