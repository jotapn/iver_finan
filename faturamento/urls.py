from django.urls import path

from .views import RegistroFaturamentoCreateView, RegistroFaturamentoListView, RegistroFaturamentoUpdateView

app_name = "faturamento"

urlpatterns = [
    path("", RegistroFaturamentoListView.as_view(), name="list"),
    path("novo/", RegistroFaturamentoCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", RegistroFaturamentoUpdateView.as_view(), name="update"),
]
