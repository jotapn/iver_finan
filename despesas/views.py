from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from .filters import DespesaFilter
from .forms import DespesaForm
from .models import Despesa
from .services import expense_chart_by_category, expense_summary_by_category


class DespesaListView(LoginRequiredMixin, ListView):
    model = Despesa
    template_name = "despesas/list.html"
    paginate_by = 30

    def get_filterset(self):
        return DespesaFilter(self.request.GET or None, queryset=Despesa.objects.select_related("categoria", "subcategoria"))

    def get_queryset(self):
        self.filterset = self.get_filterset()
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        ano = int(self.request.GET.get("ano", today.year))
        mes = int(self.request.GET.get("mes", today.month))
        context["filter"] = self.filterset
        context["chart_data"] = expense_chart_by_category(ano, mes)
        context["selected_year"] = ano
        context["selected_month"] = mes
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
