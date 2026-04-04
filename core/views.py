from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from .services import get_dashboard_context
from usuarios.permissions import module_required


@login_required
@module_required("dashboard")
def dashboard(request):
    return render(request, "dashboard.html", get_dashboard_context())


def healthcheck(request):
    return JsonResponse({"status": "ok"})

# Create your views here.
