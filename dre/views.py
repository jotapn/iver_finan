from io import BytesIO

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import TemplateView, View

from .services import annual_total, build_dre, export_dre_workbook


class DREIndexView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return redirect("dre:annual", ano=timezone.localdate().year)


class DREAnualView(LoginRequiredMixin, TemplateView):
    template_name = "dre/anual.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dre"] = build_dre(self.kwargs["ano"])
        context["annual_total"] = annual_total
        return context


class DREExportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        ano = self.kwargs["ano"]
        workbook = export_dre_workbook(build_dre(ano))
        buffer = BytesIO()
        workbook.save(buffer)
        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="dre_{ano}.xlsx"'
        return response
