from django.contrib import admin

from .models import Perfil, PerfilAcesso


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("user", "perfil_acesso", "nome_completo", "telefone", "cargo")
    search_fields = ("user__username", "nome_completo", "telefone", "cargo")


@admin.register(PerfilAcesso)
class PerfilAcessoAdmin(admin.ModelAdmin):
    list_display = ("nome", "ver_dashboard", "ver_cadastros", "ver_faturamento", "ver_despesas", "ver_folha", "ver_dre", "ver_usuarios")
    search_fields = ("nome",)
