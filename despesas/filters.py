from django import forms
import django_filters

from cadastros.models import SubcategoriaDeSpesa

from .models import Despesa
from .services import expense_period_choices


class DespesaFilter(django_filters.FilterSet):
    periodo = django_filters.ChoiceFilter(
        label="Periodo",
        method="filter_periodo",
        choices=(),
        empty_label=None,
    )
    pago = django_filters.ChoiceFilter(
        label="Status",
        method="filter_pago",
        choices=(
            ("", "Todos"),
            ("true", "Pago"),
            ("false", "Pendente"),
        ),
    )

    class Meta:
        model = Despesa
        fields = ["periodo", "categoria", "subcategoria", "pago"]

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)

        periodos = expense_period_choices()
        self.filters["periodo"].field.choices = periodos
        self.form.fields["periodo"].choices = periodos

        self.form.fields["periodo"].widget = forms.Select(attrs={"class": "form-select"})
        self.form.fields["periodo"].widget.choices = periodos
        self.form.fields["categoria"].widget.attrs["class"] = "form-select"
        self.form.fields["subcategoria"].widget.attrs["class"] = "form-select"
        self.form.fields["pago"].widget.attrs["class"] = "form-select"

        categoria_id = self.data.get("categoria") or self.form.initial.get("categoria")
        if categoria_id:
            subcategorias = SubcategoriaDeSpesa.objects.filter(categoria_id=categoria_id).order_by("nome")
            self.filters["subcategoria"].field.queryset = subcategorias
            self.form.fields["subcategoria"].queryset = subcategorias
        else:
            empty_queryset = SubcategoriaDeSpesa.objects.none()
            self.filters["subcategoria"].field.queryset = empty_queryset
            self.form.fields["subcategoria"].queryset = empty_queryset

    def filter_periodo(self, queryset, name, value):
        try:
            ano_str, mes_str = value.split("-")
            ano = int(ano_str)
            mes = int(mes_str)
        except (ValueError, AttributeError):
            return queryset
        return queryset.filter(ano_referencia=ano, mes_referencia=mes)

    def filter_pago(self, queryset, name, value):
        if value == "true":
            return queryset.filter(pago=True)
        if value == "false":
            return queryset.filter(pago=False)
        return queryset
