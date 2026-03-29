from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import BeneficioColaboradorForm, DespesaTrabalhistaMensalForm, LancamentoColaboradorForm, PeriodoFolhaForm
from .models import BeneficioColaborador, DespesaTrabalhistaMensal, LancamentoColaborador, PeriodoFolha
from .services import resumo_despesas_trabalhistas, sync_periodo


class PeriodoFolhaListView(LoginRequiredMixin, ListView):
    model = PeriodoFolha
    template_name = "folha/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PeriodoFolhaForm()
        return context


class PeriodoFolhaCreateView(LoginRequiredMixin, CreateView):
    model = PeriodoFolha
    form_class = PeriodoFolhaForm
    success_url = reverse_lazy("folha:index")

    def form_valid(self, form):
        response = super().form_valid(form)
        sync_periodo(self.object)
        return response


class PeriodoFolhaDetailView(LoginRequiredMixin, DetailView):
    model = PeriodoFolha
    template_name = "folha/painel.html"
    context_object_name = "periodo"

    def get_object(self, queryset=None):
        periodo = get_object_or_404(PeriodoFolha, ano=self.kwargs["ano"], mes=self.kwargs["mes"])
        sync_periodo(periodo)
        return periodo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periodo = self.object
        context["lancamentos"] = periodo.lancamentos.select_related("colaborador", "colaborador__cargo", "colaborador__cargo__setor")
        context["beneficios"] = periodo.beneficios.select_related("colaborador")
        context["despesas_trabalhistas"] = periodo.despesas_trabalhistas.select_related("banco")
        context["resumo_trabalhista"] = resumo_despesas_trabalhistas(periodo)
        return context


class LancamentoColaboradorUpdateView(LoginRequiredMixin, UpdateView):
    model = LancamentoColaborador
    form_class = LancamentoColaboradorForm
    template_name = "folha/lancamento_form.html"

    def get_success_url(self):
        return reverse("folha:detail", kwargs={"ano": self.object.periodo.ano, "mes": self.object.periodo.mes})


class ColaboradorHistoricoView(LoginRequiredMixin, ListView):
    template_name = "folha/colaborador_historico.html"
    context_object_name = "historico"

    def get_queryset(self):
        return LancamentoColaborador.objects.filter(colaborador_id=self.kwargs["pk"]).select_related("periodo", "colaborador")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["colaborador"] = self.get_queryset().first().colaborador if self.get_queryset() else None
        return context


class PeriodoFormMixin(LoginRequiredMixin):
    periodo = None

    def dispatch(self, request, *args, **kwargs):
        self.periodo = get_object_or_404(PeriodoFolha, ano=kwargs["ano"], mes=kwargs["mes"])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("folha:detail", kwargs={"ano": self.periodo.ano, "mes": self.periodo.mes})


class BeneficioCreateView(PeriodoFormMixin, CreateView):
    model = BeneficioColaborador
    form_class = BeneficioColaboradorForm
    template_name = "folha/beneficio_form.html"

    def form_valid(self, form):
        form.instance.periodo = self.periodo
        return super().form_valid(form)


class DespesaTrabalhistaCreateView(PeriodoFormMixin, CreateView):
    model = DespesaTrabalhistaMensal
    form_class = DespesaTrabalhistaMensalForm
    template_name = "folha/despesa_trabalhista_form.html"

    def form_valid(self, form):
        form.instance.periodo = self.periodo
        return super().form_valid(form)


@login_required
def marcar_lancamento_pago(request, pk, campo):
    lancamento = get_object_or_404(LancamentoColaborador, pk=pk)
    campos_validos = {
        "adiantamento": ("adiantamento_pago", "adiantamento_data"),
        "saldo-final": ("saldo_final_pago", "saldo_final_data"),
        "produtividade-1": ("produtividade_1_pago", "produtividade_1_data"),
        "produtividade-2": ("produtividade_2_pago", "produtividade_2_data"),
    }
    if campo not in campos_validos:
        raise Http404("Pagamento inválido.")
    if request.method == "POST":
        pago_field, data_field = campos_validos[campo]
        setattr(lancamento, pago_field, True)
        setattr(lancamento, data_field, timezone.localdate())
        lancamento.save(update_fields=[pago_field, data_field])
    return redirect("folha:detail", ano=lancamento.periodo.ano, mes=lancamento.periodo.mes)


@login_required
def marcar_beneficio_pago(request, pk):
    beneficio = get_object_or_404(BeneficioColaborador, pk=pk)
    if request.method == "POST":
        beneficio.pago = True
        beneficio.data_pagamento = timezone.localdate()
        beneficio.save(update_fields=["pago", "data_pagamento"])
    return redirect("folha:detail", ano=beneficio.periodo.ano, mes=beneficio.periodo.mes)

# Create your views here.
