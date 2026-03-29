from django.contrib import admin

from .models import RegistroFaturamento


@admin.register(RegistroFaturamento)
class RegistroFaturamentoAdmin(admin.ModelAdmin):
    list_display = ("data", "total", "faturamento_bar", "faturamento_cozinha")
    list_filter = ("data",)
    search_fields = ("observacao",)

# Register your models here.
