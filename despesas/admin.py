from django.contrib import admin

from .models import Despesa, RecorrenciaDespesa


@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ("descricao", "categoria", "subcategoria", "valor", "mes_referencia", "ano_referencia", "pago", "recorrencia")
    list_filter = ("categoria", "subcategoria", "pago", "mes_referencia", "ano_referencia")
    search_fields = ("descricao", "observacao")


@admin.register(RecorrenciaDespesa)
class RecorrenciaDespesaAdmin(admin.ModelAdmin):
    list_display = ("descricao", "categoria", "subcategoria", "valor", "data_inicio", "data_fim", "ativa")
    list_filter = ("categoria", "subcategoria", "ativa")
    search_fields = ("descricao", "observacao")
