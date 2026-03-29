from django.urls import path

from .views import CadastroCreateView, CadastroDeleteView, CadastroIndexView, CadastroListView, CadastroUpdateView

app_name = "cadastros"

urlpatterns = [
    path("", CadastroIndexView.as_view(), name="index"),
    path("<slug:model_slug>/", CadastroListView.as_view(), name="list"),
    path("<slug:model_slug>/novo/", CadastroCreateView.as_view(), name="create"),
    path("<slug:model_slug>/<int:pk>/editar/", CadastroUpdateView.as_view(), name="update"),
    path("<slug:model_slug>/<int:pk>/excluir/", CadastroDeleteView.as_view(), name="delete"),
]
