from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services import get_dashboard_context


@login_required
def dashboard(request):
    return render(request, "dashboard.html", get_dashboard_context())

# Create your views here.
