from django.urls import path

from .views import (
    BeneficioCreateView,
    ColaboradorHistoricoView,
    LancamentoColaboradorUpdateView,
    PeriodoFolhaCreateView,
    PeriodoFolhaDetailView,
    PeriodoFolhaListView,
    marcar_beneficio_pago,
    marcar_lancamento_pago,
)

app_name = "folha"

urlpatterns = [
    path("", PeriodoFolhaListView.as_view(), name="index"),
    path("novo/", PeriodoFolhaCreateView.as_view(), name="create"),
    path("<int:ano>/<int:mes>/", PeriodoFolhaDetailView.as_view(), name="detail"),
    path("<int:ano>/<int:mes>/colaborador/<int:pk>/", LancamentoColaboradorUpdateView.as_view(), name="update-lancamento"),
    path("<int:ano>/<int:mes>/colaborador/<int:pk>/historico/", ColaboradorHistoricoView.as_view(), name="history"),
    path("<int:ano>/<int:mes>/beneficio/novo/", BeneficioCreateView.as_view(), name="create-benefit"),
    path("lancamento/<int:pk>/pagar/<slug:campo>/", marcar_lancamento_pago, name="mark-launch-paid"),
    path("beneficio/<int:pk>/pagar/", marcar_beneficio_pago, name="mark-benefit-paid"),
]
