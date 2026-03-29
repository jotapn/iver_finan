from django.contrib import admin

from .models import Banco, Cargo, CategoriaDeSpesa, Colaborador, FormaPagamento, Setor, SubcategoriaDeSpesa


@admin.register(Banco)
class BancoAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)


@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ("nome", "setor", "comissao_percentual")
    list_filter = ("setor",)
    search_fields = ("nome",)


@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ("nome", "documento", "telefone", "email", "cargo", "ativo", "data_admissao", "data_demissao")
    list_filter = ("ativo", "cargo__setor")
    search_fields = ("nome", "documento", "telefone", "email", "cargo__nome")


@admin.register(FormaPagamento)
class FormaPagamentoAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)


@admin.register(CategoriaDeSpesa)
class CategoriaDeSpesaAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)


@admin.register(SubcategoriaDeSpesa)
class SubcategoriaDeSpesaAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria")
    list_filter = ("categoria",)
    search_fields = ("nome", "categoria__nome")

# Register your models here.
