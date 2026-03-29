import django_filters

from .models import Despesa


class DespesaFilter(django_filters.FilterSet):
    mes = django_filters.NumberFilter(field_name="mes_referencia", label="Mês")
    ano = django_filters.NumberFilter(field_name="ano_referencia", label="Ano")

    class Meta:
        model = Despesa
        fields = ["mes", "ano", "categoria", "subcategoria", "pago"]
