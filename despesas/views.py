from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from usuarios.permissions import ModuleAccessMixin, module_required

from .filters import DespesaFilter
from .forms import DespesaForm
from .models import Despesa
from .services import (
    create_or_update_recurrence,
    expense_chart_by_category,
    expense_chart_by_subcategory,
    expense_period_choices,
    expense_summary_by_category,
    generate_recurring_expenses_until,
    grouped_subcategory_options,
    top_subcategories,
)


class DespesaListView(ModuleAccessMixin, LoginRequiredMixin, ListView):
    model = Despesa
    template_name = "despesas/list.html"
    paginate_by = 30
    required_module = "despesas"
    allowed_ordering = {
        "descricao": "descricao",
        "subcategoria": "subcategoria__nome",
        "vencimento": "data_vencimento",
        "pagamento": "data_pagamento",
        "valor": "valor",
        "status": "pago",
    }

    def get_default_period(self):
        latest = expense_period_choices()[:1]
        if latest:
            return latest[0][0]
        today = timezone.localdate()
        return f"{today.year:04d}-{today.month:02d}"

    def get_filterset(self):
        data = self.request.GET.copy()
        if not data.get("periodo"):
            data["periodo"] = self.get_default_period()
        ano_str, mes_str = data["periodo"].split("-")
        generate_recurring_expenses_until(int(ano_str), int(mes_str))
        return DespesaFilter(
            data,
            queryset=Despesa.objects.select_related("categoria", "subcategoria", "recorrencia"),
        )

    def get_queryset(self):
        self.filterset = self.get_filterset()
        queryset = self.filterset.qs
        ordering = self.request.GET.get("ordenar", "-id")
        descending = ordering.startswith("-")
        ordering_key = ordering[1:] if descending else ordering

        if ordering_key == "id":
            self.current_ordering = ordering
            return queryset.order_by("-id" if descending else "id")

        ordering_field = self.allowed_ordering.get(ordering_key)
        if not ordering_field:
            self.current_ordering = "-id"
            return queryset.order_by("-id")

        if ordering_field in {"data_vencimento", "data_pagamento"}:
            expression = F(ordering_field)
            queryset = queryset.order_by(
                expression.desc(nulls_last=True) if descending else expression.asc(nulls_last=True),
                "-id",
            )
        else:
            prefix = "-" if descending else ""
            queryset = queryset.order_by(f"{prefix}{ordering_field}", "-id")

        self.current_ordering = f"-{ordering_key}" if descending else ordering_key
        return queryset

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
        ordering_params = self.request.GET.copy()
        ordering_params.pop("ordenar", None)
        ordering_params.pop("page", None)
        pagination_params = self.request.GET.copy()
        pagination_params.pop("page", None)
        context["ordering_base_query"] = ordering_params.urlencode()
        context["pagination_base_query"] = pagination_params.urlencode()
        context["current_ordering"] = getattr(self, "current_ordering", "-id")
        context["subcategory_options"] = grouped_subcategory_options()
        return context


class DespesaCreateView(ModuleAccessMixin, LoginRequiredMixin, CreateView):
    model = Despesa
    form_class = DespesaForm
    template_name = "despesas/form.html"
    success_url = reverse_lazy("despesas:list")
    required_module = "despesas"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subcategory_options"] = grouped_subcategory_options()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        recorrencia = create_or_update_recurrence(
            self.object,
            recorrente=form.cleaned_data["recorrente"],
            recorrencia_ativa=form.cleaned_data.get("recorrencia_ativa", True),
            recorrencia_data_fim=form.cleaned_data["recorrencia_data_fim"],
        )
        if recorrencia:
            target = recorrencia.data_fim or timezone.localdate()
            generate_recurring_expenses_until(target.year, target.month)
        return response


class DespesaUpdateView(ModuleAccessMixin, LoginRequiredMixin, UpdateView):
    model = Despesa
    form_class = DespesaForm
    template_name = "despesas/form.html"
    success_url = reverse_lazy("despesas:list")
    required_module = "despesas"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.origem == Despesa.Origem.FOLHA:
            messages.warning(request, "Despesas geradas pela folha nao podem ser editadas manualmente.")
            return redirect("despesas:list")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subcategory_options"] = grouped_subcategory_options()
        context["recurrence_info"] = self.object.recorrencia
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        recorrencia = create_or_update_recurrence(
            self.object,
            recorrente=form.cleaned_data["recorrente"],
            recorrencia_ativa=form.cleaned_data.get("recorrencia_ativa", True),
            recorrencia_data_fim=form.cleaned_data["recorrencia_data_fim"],
        )
        if recorrencia and recorrencia.ativa:
            target = recorrencia.data_fim or timezone.localdate()
            generate_recurring_expenses_until(target.year, target.month)
        return response


class DespesaDeleteView(ModuleAccessMixin, LoginRequiredMixin, DeleteView):
    model = Despesa
    template_name = "confirm_delete.html"
    success_url = reverse_lazy("despesas:list")
    required_module = "despesas"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.origem == Despesa.Origem.FOLHA:
            messages.warning(request, "Despesas geradas pela folha nao podem ser excluidas manualmente.")
            return redirect("despesas:list")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recurrence_info"] = self.object.recorrencia
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        recurrence = self.object.recorrencia
        if recurrence and recurrence.ativa:
            recurrence.ativa = False
            recurrence.save(update_fields=["ativa"])
        return super().post(request, *args, **kwargs)


class DespesaResumoView(ModuleAccessMixin, LoginRequiredMixin, TemplateView):
    template_name = "despesas/resumo.html"
    required_module = "despesas"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        ano = int(self.request.GET.get("ano", today.year))
        mes = int(self.request.GET.get("mes", today.month))
        generate_recurring_expenses_until(ano, mes)
        context["resumo"] = expense_summary_by_category(ano, mes)
        context["ano"] = ano
        context["mes"] = mes
        context["periodo"] = f"{ano:04d}-{mes:02d}"
        return context


@login_required
@module_required("despesas")
def marcar_despesa_paga(request, pk):
    despesa = get_object_or_404(Despesa, pk=pk)
    if despesa.origem == Despesa.Origem.FOLHA:
        messages.warning(request, "Pagamentos gerados pela folha devem ser controlados na propria folha.")
        return redirect("despesas:list")
    if request.method == "POST":
        despesa.pago = True
        despesa.data_pagamento = timezone.localdate()
        despesa.save(update_fields=["pago", "data_pagamento"])
    return redirect("despesas:list")

# Create your views here.
