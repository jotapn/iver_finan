from django.urls import path

from .views import DespesaCreateView, DespesaDeleteView, DespesaListView, DespesaResumoView, DespesaUpdateView, marcar_despesa_paga

app_name = "despesas"

urlpatterns = [
    path("", DespesaListView.as_view(), name="list"),
    path("nova/", DespesaCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", DespesaUpdateView.as_view(), name="update"),
    path("<int:pk>/excluir/", DespesaDeleteView.as_view(), name="delete"),
    path("<int:pk>/pagar/", marcar_despesa_paga, name="mark-paid"),
    path("resumo/", DespesaResumoView.as_view(), name="summary"),
]
