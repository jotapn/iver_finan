import django_filters

from .models import RegistroFaturamento


class RegistroFaturamentoFilter(django_filters.FilterSet):
    ano = django_filters.NumberFilter(field_name="data", lookup_expr="year", label="Ano")
    mes = django_filters.NumberFilter(field_name="data", lookup_expr="month", label="Mês")

    class Meta:
        model = RegistroFaturamento
        fields = ["ano", "mes"]
