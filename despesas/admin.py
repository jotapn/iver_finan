from django.contrib import admin

from .models import Despesa


@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ("descricao", "categoria", "subcategoria", "valor", "mes_referencia", "ano_referencia", "pago")
    list_filter = ("categoria", "subcategoria", "pago", "mes_referencia", "ano_referencia")
    search_fields = ("descricao", "observacao")

# Register your models here.
