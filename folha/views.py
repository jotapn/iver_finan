from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from usuarios.permissions import ModuleAccessMixin, module_required

from .forms import BeneficioColaboradorForm, LancamentoColaboradorForm, PeriodoFolhaForm
from .models import BeneficioColaborador, LancamentoColaborador, PeriodoFolha
from .services import sync_periodo


class PeriodoFolhaListView(ModuleAccessMixin, LoginRequiredMixin, ListView):
    model = PeriodoFolha
    template_name = "folha/index.html"
    required_module = "folha"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PeriodoFolhaForm()
        return context


class PeriodoFolhaCreateView(ModuleAccessMixin, LoginRequiredMixin, CreateView):
    model = PeriodoFolha
    form_class = PeriodoFolhaForm
    success_url = reverse_lazy("folha:index")
    required_module = "folha"

    def form_valid(self, form):
        response = super().form_valid(form)
        sync_periodo(self.object)
        return response


class PeriodoFolhaDetailView(ModuleAccessMixin, LoginRequiredMixin, DetailView):
    model = PeriodoFolha
    template_name = "folha/painel.html"
    context_object_name = "periodo"
    required_module = "folha"

    def get_object(self, queryset=None):
        periodo = get_object_or_404(PeriodoFolha, ano=self.kwargs["ano"], mes=self.kwargs["mes"])
        sync_periodo(periodo)
        return periodo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periodo = self.object
        lancamentos = list(periodo.lancamentos.select_related("colaborador", "colaborador__cargo", "colaborador__cargo__setor"))
        for lancamento in lancamentos:
            lancamento.inline_form = LancamentoColaboradorForm(instance=lancamento, prefix=f"lanc-{lancamento.pk}")
        context["lancamentos"] = lancamentos
        context["beneficios"] = periodo.beneficios.select_related("colaborador")
        return context


class LancamentoColaboradorUpdateView(ModuleAccessMixin, LoginRequiredMixin, UpdateView):
    model = LancamentoColaborador
    form_class = LancamentoColaboradorForm
    template_name = "folha/lancamento_form.html"
    required_module = "folha"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == "POST" and self.request.POST.get("inline") == "1":
            kwargs["prefix"] = f"lanc-{self.object.pk}"
        return kwargs

    def get_success_url(self):
        return reverse("folha:detail", kwargs={"ano": self.object.periodo.ano, "mes": self.object.periodo.mes})


class ColaboradorHistoricoView(ModuleAccessMixin, LoginRequiredMixin, ListView):
    template_name = "folha/colaborador_historico.html"
    context_object_name = "historico"
    required_module = "folha"

    def get_queryset(self):
        return LancamentoColaborador.objects.filter(colaborador_id=self.kwargs["pk"]).select_related("periodo", "colaborador")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["colaborador"] = self.get_queryset().first().colaborador if self.get_queryset() else None
        return context


class PeriodoFormMixin(ModuleAccessMixin, LoginRequiredMixin):
    periodo = None
    required_module = "folha"

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


@login_required
@module_required("folha")
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
        if getattr(lancamento, pago_field):
            setattr(lancamento, pago_field, False)
            setattr(lancamento, data_field, None)
        else:
            setattr(lancamento, pago_field, True)
            setattr(lancamento, data_field, timezone.localdate())
        lancamento.save(update_fields=[pago_field, data_field])
    return redirect("folha:detail", ano=lancamento.periodo.ano, mes=lancamento.periodo.mes)


@login_required
@module_required("folha")
def marcar_beneficio_pago(request, pk):
    beneficio = get_object_or_404(BeneficioColaborador, pk=pk)
    if request.method == "POST":
        if beneficio.pago:
            beneficio.pago = False
            beneficio.data_pagamento = None
        else:
            beneficio.pago = True
            beneficio.data_pagamento = timezone.localdate()
        beneficio.save(update_fields=["pago", "data_pagamento"])
    return redirect("folha:detail", ano=beneficio.periodo.ano, mes=beneficio.periodo.mes)

# Create your views here.
