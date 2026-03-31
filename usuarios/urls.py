from django.urls import path

from .views import (
    ConfiguracaoIndexView,
    PerfilAcessoListView,
    PerfilAcessoCreateView,
    PerfilAcessoUpdateView,
    PerfilUpdateView,
    UsuarioCreateView,
    UsuarioListView,
    UsuarioUpdateView,
)

app_name = "usuarios"

urlpatterns = [
    path("", ConfiguracaoIndexView.as_view(), name="index"),
    path("usuarios/", UsuarioListView.as_view(), name="list"),
    path("novo/", UsuarioCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", UsuarioUpdateView.as_view(), name="update"),
    path("perfil/<int:pk>/editar/", PerfilUpdateView.as_view(), name="profile-update"),
    path("perfis/", PerfilAcessoListView.as_view(), name="access-profile-list"),
    path("perfis/novo/", PerfilAcessoCreateView.as_view(), name="access-profile-create"),
    path("perfis/<int:pk>/editar/", PerfilAcessoUpdateView.as_view(), name="access-profile-update"),
]
