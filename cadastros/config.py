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
    "colaboradores": {
        "model": Colaborador,
        "form": ColaboradorForm,
        "title": "Colaboradores",
        "list_fields": [
            {"name": "nome", "label": "Nome"},
            {"name": "documento", "label": "Documento"},
            {"name": "telefone", "label": "Telefone"},
            {"name": "email", "label": "Email"},
            {"name": "cargo", "label": "Cargo"},
            {"name": "setor", "label": "Setor"},
            {"name": "ativo", "label": "Ativo"},
            {"name": "data_admissao", "label": "Data de admissao"},
            {"name": "data_demissao", "label": "Data de demissao"},
        ],
    },
    "formas-pagamento": {"model": FormaPagamento, "form": FormaPagamentoForm, "title": "Formas de pagamento"},
    "categorias-despesa": {"model": CategoriaDeSpesa, "form": CategoriaDeSpesaForm, "title": "Categorias de despesa"},
    "subcategorias-despesa": {
        "model": SubcategoriaDeSpesa,
        "form": SubcategoriaDeSpesaForm,
        "title": "Subcategorias de despesa",
    },
}
