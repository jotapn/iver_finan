from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from usuarios.permissions import ModuleAccessMixin

from .filters import RegistroFaturamentoFilter
from .forms import RegistroFaturamentoForm
from .models import RegistroFaturamento
from .services import monthly_summary


class RegistroFaturamentoListView(ModuleAccessMixin, LoginRequiredMixin, ListView):
    model = RegistroFaturamento
    template_name = "faturamento/list.html"
    paginate_by = 31
    required_module = "faturamento"

    def get_filterset(self):
        return RegistroFaturamentoFilter(self.request.GET or None, queryset=RegistroFaturamento.objects.all())

    def get_queryset(self):
        self.filterset = self.get_filterset()
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        mes = int(self.request.GET.get("mes", 0) or 0)
        ano = int(self.request.GET.get("ano", 0) or 0)
        if not mes or not ano:
            primeiro = self.object_list.first()
            if primeiro:
                mes, ano = primeiro.data.month, primeiro.data.year
        context["resumo"] = monthly_summary(ano, mes) if mes and ano else None
        return context


class RegistroFaturamentoCreateView(ModuleAccessMixin, LoginRequiredMixin, CreateView):
    model = RegistroFaturamento
    form_class = RegistroFaturamentoForm
    template_name = "faturamento/form.html"
    success_url = reverse_lazy("faturamento:list")
    required_module = "faturamento"


class RegistroFaturamentoUpdateView(ModuleAccessMixin, LoginRequiredMixin, UpdateView):
    model = RegistroFaturamento
    form_class = RegistroFaturamentoForm
    template_name = "faturamento/form.html"
    success_url = reverse_lazy("faturamento:list")
    required_module = "faturamento"

# Create your views here.
