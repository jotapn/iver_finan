from django import forms
import django_filters

from cadastros.models import SubcategoriaDeSpesa

from .models import Despesa


MONTH_LABELS = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}


class DespesaFilter(django_filters.FilterSet):
    periodo = django_filters.ChoiceFilter(
        label="Período",
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

        periodos = [
            (f"{ano:04d}-{mes:02d}", f"{MONTH_LABELS.get(mes, mes)}/{ano}")
            for ano, mes in (
                Despesa.objects.values_list("ano_referencia", "mes_referencia")
                .distinct()
                .order_by("-ano_referencia", "-mes_referencia")
            )
        ]
        self.filters["periodo"].field.choices = periodos
        self.form.fields["periodo"].choices = periodos

        self.form.fields["periodo"].widget = forms.Select(attrs={"class": "form-select"})
        self.form.fields["periodo"].widget.choices = periodos
        self.form.fields["categoria"].widget.attrs["class"] = "form-select"
        self.form.fields["subcategoria"].widget.attrs["class"] = "form-select"
        self.form.fields["pago"].widget.attrs["class"] = "form-select"

        categoria_id = self.data.get("categoria") or self.form.initial.get("categoria")
        if categoria_id:
            self.filters["subcategoria"].field.queryset = SubcategoriaDeSpesa.objects.filter(categoria_id=categoria_id)
            self.form.fields["subcategoria"].queryset = SubcategoriaDeSpesa.objects.filter(categoria_id=categoria_id)
        else:
            self.filters["subcategoria"].field.queryset = SubcategoriaDeSpesa.objects.all()
            self.form.fields["subcategoria"].queryset = SubcategoriaDeSpesa.objects.all()

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
