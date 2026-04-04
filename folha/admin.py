from django.contrib import admin

from .models import BeneficioColaborador, LancamentoColaborador, PeriodoFolha


@admin.register(PeriodoFolha)
class PeriodoFolhaAdmin(admin.ModelAdmin):
    list_display = ("mes", "ano", "faturamento_total")
    list_filter = ("ano", "mes")
    search_fields = ("ano",)


@admin.register(LancamentoColaborador)
class LancamentoColaboradorAdmin(admin.ModelAdmin):
    list_display = ("colaborador", "periodo", "salario_bruto", "consumo_colaborador", "saldo_final_valor", "adiantamento_pago", "saldo_final_pago")
    list_filter = ("periodo__ano", "periodo__mes", "colaborador__cargo__setor")
    search_fields = ("colaborador__nome",)


@admin.register(BeneficioColaborador)
class BeneficioColaboradorAdmin(admin.ModelAdmin):
    list_display = ("colaborador", "periodo", "vale_transporte", "ajuda_custo", "pago")
    list_filter = ("periodo__ano", "periodo__mes", "pago")
    search_fields = ("colaborador__nome",)
