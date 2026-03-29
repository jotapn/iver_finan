from .forms import (
    BancoForm,
    CargoForm,
    CategoriaDeSpesaForm,
    ColaboradorForm,
    FormaPagamentoForm,
    SetorForm,
    SubcategoriaDeSpesaForm,
)
from .models import Banco, Cargo, CategoriaDeSpesa, Colaborador, FormaPagamento, Setor, SubcategoriaDeSpesa

CADASTRO_CONFIG = {
    "bancos": {"model": Banco, "form": BancoForm, "title": "Bancos"},
    "setores": {"model": Setor, "form": SetorForm, "title": "Setores"},
    "cargos": {"model": Cargo, "form": CargoForm, "title": "Cargos"},
    "colaboradores": {"model": Colaborador, "form": ColaboradorForm, "title": "Colaboradores"},
    "formas-pagamento": {"model": FormaPagamento, "form": FormaPagamentoForm, "title": "Formas de pagamento"},
    "categorias-despesa": {"model": CategoriaDeSpesa, "form": CategoriaDeSpesaForm, "title": "Categorias de despesa"},
    "subcategorias-despesa": {
        "model": SubcategoriaDeSpesa,
        "form": SubcategoriaDeSpesaForm,
        "title": "Subcategorias de despesa",
    },
}
