from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from .forms import PerfilAcessoForm, PerfilForm, UsuarioCreateForm, UsuarioUpdateForm
from .models import Perfil, PerfilAcesso
from .permissions import ModuleAccessMixin

User = get_user_model()


class ConfiguracaoIndexView(ModuleAccessMixin, LoginRequiredMixin, TemplateView):
    template_name = "usuarios/index.html"
    required_module = "usuarios"


class UsuarioListView(ModuleAccessMixin, LoginRequiredMixin, ListView):
    model = User
    template_name = "usuarios/list.html"
    context_object_name = "usuarios"
    paginate_by = 20
    required_module = "usuarios"

    def get_queryset(self):
        for user in User.objects.filter(perfil__isnull=True):
            Perfil.objects.get_or_create(user=user)
        return User.objects.select_related("perfil", "perfil__perfil_acesso").order_by("username")


class PerfilAcessoListView(ModuleAccessMixin, LoginRequiredMixin, ListView):
    model = PerfilAcesso
    template_name = "usuarios/perfil_acesso_list.html"
    context_object_name = "perfis_acesso"
    paginate_by = 20
    required_module = "usuarios"


class UsuarioCreateView(ModuleAccessMixin, LoginRequiredMixin, CreateView):
    model = User
    form_class = UsuarioCreateForm
    template_name = "usuarios/form.html"
    success_url = reverse_lazy("usuarios:list")
    required_module = "usuarios"


class UsuarioUpdateView(ModuleAccessMixin, LoginRequiredMixin, UpdateView):
    model = User
    form_class = UsuarioUpdateForm
    template_name = "usuarios/form.html"
    success_url = reverse_lazy("usuarios:list")
    required_module = "usuarios"


class PerfilUpdateView(ModuleAccessMixin, LoginRequiredMixin, UpdateView):
    model = Perfil
    form_class = PerfilForm
    template_name = "usuarios/perfil_form.html"
    success_url = reverse_lazy("usuarios:list")
    required_module = "usuarios"


class PerfilAcessoCreateView(ModuleAccessMixin, LoginRequiredMixin, CreateView):
    model = PerfilAcesso
    form_class = PerfilAcessoForm
    template_name = "usuarios/perfil_acesso_form.html"
    success_url = reverse_lazy("usuarios:access-profile-list")
    required_module = "usuarios"


class PerfilAcessoUpdateView(ModuleAccessMixin, LoginRequiredMixin, UpdateView):
    model = PerfilAcesso
    form_class = PerfilAcessoForm
    template_name = "usuarios/perfil_acesso_form.html"
    success_url = reverse_lazy("usuarios:access-profile-list")
    required_module = "usuarios"
