from django.urls import path

from .views import DREAnualView, DREExportView, DREIndexView

app_name = "dre"

urlpatterns = [
    path("", DREIndexView.as_view(), name="index"),
    path("<int:ano>/", DREAnualView.as_view(), name="annual"),
    path("<int:ano>/exportar/", DREExportView.as_view(), name="export"),
]
