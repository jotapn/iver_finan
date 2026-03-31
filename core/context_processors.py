from cadastros.config import CADASTRO_CONFIG
from usuarios.permissions import has_module_access


def sidebar_cadastros(request):
    return {
        "sidebar_cadastros": CADASTRO_CONFIG,
        "module_access": {
            "dashboard": has_module_access(request.user, "dashboard"),
            "cadastros": has_module_access(request.user, "cadastros"),
            "faturamento": has_module_access(request.user, "faturamento"),
            "despesas": has_module_access(request.user, "despesas"),
            "folha": has_module_access(request.user, "folha"),
            "dre": has_module_access(request.user, "dre"),
            "usuarios": has_module_access(request.user, "usuarios"),
            "admin": has_module_access(request.user, "admin"),
        },
    }
