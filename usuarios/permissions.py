from functools import wraps

from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied


MODULE_FIELD_MAP = {
    "dashboard": "ver_dashboard",
    "cadastros": "ver_cadastros",
    "faturamento": "ver_faturamento",
    "despesas": "ver_despesas",
    "folha": "ver_folha",
    "dre": "ver_dre",
    "usuarios": "ver_usuarios",
    "admin": "ver_admin",
}


def get_module_access_map(user):
    cached = getattr(user, "_module_access_map", None)
    if cached is not None:
        return cached

    if not getattr(user, "is_authenticated", False):
        cached = {module: False for module in MODULE_FIELD_MAP}
    elif getattr(user, "is_superuser", False):
        cached = {module: True for module in MODULE_FIELD_MAP}
    else:
        perfil = getattr(user, "perfil", None)
        perfil_acesso = getattr(perfil, "perfil_acesso", None)
        if perfil_acesso is None:
            cached = {module: True for module in MODULE_FIELD_MAP}
        else:
            cached = {
                module: getattr(perfil_acesso, field_name, False)
                for module, field_name in MODULE_FIELD_MAP.items()
            }

    setattr(user, "_module_access_map", cached)
    return cached


def has_module_access(user, module):
    field_name = MODULE_FIELD_MAP.get(module)
    if not field_name:
        return True
    return get_module_access_map(user).get(module, False)


class ModuleAccessMixin(AccessMixin):
    required_module = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.required_module and not has_module_access(request.user, self.required_module):
            raise PermissionDenied("Voce nao tem permissao para acessar este modulo.")
        return super().dispatch(request, *args, **kwargs)


def module_required(module):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not has_module_access(request.user, module):
                raise PermissionDenied("Voce nao tem permissao para acessar este modulo.")
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
