from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from cadastros.models import SubcategoriaDeSpesa

from .filters import DespesaFilter
from .forms import DespesaForm
from .models import Despesa
from .services import expense_chart_by_category, expense_chart_by_subcategory, expense_summary_by_category, top_subcategories


class DespesaListView(LoginRequiredMixin, ListView):
    model = Despesa
    template_name = "despesas/list.html"
    paginate_by = 30

    def get_default_period(self):
        latest = (
            Despesa.objects.values_list("ano_referencia", "mes_referencia")
            .distinct()
            .order_by("-ano_referencia", "-mes_referencia")
            .first()
        )
        if latest:
            ano, mes = latest
            return f"{ano:04d}-{mes:02d}"
        today = timezone.localdate()
        return f"{today.year:04d}-{today.month:02d}"

    def get_filterset(self):
        data = self.request.GET.copy()
        if not data.get("periodo"):
            data["periodo"] = self.get_default_period()
        return DespesaFilter(data, queryset=Despesa.objects.select_related("categoria", "subcategoria"))

    def get_queryset(self):
        self.filterset = self.get_filterset()
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periodo = self.request.GET.get("periodo") or self.get_default_period()
        ano_str, mes_str = periodo.split("-")
        ano = int(ano_str)
        mes = int(mes_str)
        context["filter"] = self.filterset
        context["chart_data"] = expense_chart_by_category(ano, mes)
        context["subcategory_chart_data"] = expense_chart_by_subcategory(ano, mes)
        context["top_subcategories"] = top_subcategories(ano, mes)
        context["selected_year"] = ano
        context["selected_month"] = mes
        context["subcategory_options"] = {
            str(categoria_id): [
                {"id": str(item["id"]), "nome": item["nome"]}
                for item in SubcategoriaDeSpesa.objects.filter(categoria_id=categoria_id)
                .values("id", "nome")
                .order_by("nome")
            ]
            for categoria_id in SubcategoriaDeSpesa.objects.values_list("categoria_id", flat=True).distinct()
        }
        return context


class DespesaCreateView(LoginRequiredMixin, CreateView):
    model = Despesa
    form_class = DespesaForm
    template_name = "despesas/form.html"
    success_url = reverse_lazy("despesas:list")


class DespesaUpdateView(LoginRequiredMixin, UpdateView):
    model = Despesa
    form_class = DespesaForm
    template_name = "despesas/form.html"
    success_url = reverse_lazy("despesas:list")


class DespesaDeleteView(LoginRequiredMixin, DeleteView):
    model = Despesa
    template_name = "confirm_delete.html"
    success_url = reverse_lazy("despesas:list")


class DespesaResumoView(LoginRequiredMixin, TemplateView):
    template_name = "despesas/resumo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        ano = int(self.request.GET.get("ano", today.year))
        mes = int(self.request.GET.get("mes", today.month))
        context["resumo"] = expense_summary_by_category(ano, mes)
        context["ano"] = ano
        context["mes"] = mes
        return context


@login_required
def marcar_despesa_paga(request, pk):
    despesa = get_object_or_404(Despesa, pk=pk)
    if request.method == "POST":
        despesa.pago = True
        despesa.data_pagamento = timezone.localdate()
        despesa.save(update_fields=["pago", "data_pagamento"])
    return redirect("despesas:list")

# Create your views here.
