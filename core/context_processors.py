from cadastros.config import CADASTRO_CONFIG
from usuarios.permissions import get_module_access_map


def sidebar_cadastros(request):
    return {
        "sidebar_cadastros": CADASTRO_CONFIG,
        "module_access": get_module_access_map(request.user),
    }
