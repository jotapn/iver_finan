from decimal import Decimal

from django.db.models import Sum

from .models import Despesa


def expense_summary_by_category(year: int, month: int):
    return (
        Despesa.objects.filter(ano_referencia=year, mes_referencia=month)
        .values("categoria__nome", "subcategoria__nome")
        .annotate(total=Sum("valor"))
        .order_by("categoria__nome", "subcategoria__nome")
    )


def expense_chart_by_category(year: int, month: int) -> dict:
    items = (
        Despesa.objects.filter(ano_referencia=year, mes_referencia=month)
        .values("categoria__nome")
        .annotate(total=Sum("valor"))
        .order_by("categoria__nome")
    )
    return {
        "labels": [item["categoria__nome"] for item in items],
        "values": [float(item["total"] or Decimal("0.00")) for item in items],
    }


def expense_chart_by_subcategory(year: int, month: int) -> dict:
    items = (
        Despesa.objects.filter(ano_referencia=year, mes_referencia=month)
        .values("subcategoria__nome")
        .annotate(total=Sum("valor"))
        .order_by("subcategoria__nome")
    )
    return {
        "labels": [item["subcategoria__nome"] for item in items],
        "values": [float(item["total"] or Decimal("0.00")) for item in items],
    }


def top_subcategories(year: int, month: int, limit: int = 10):
    return (
        Despesa.objects.filter(ano_referencia=year, mes_referencia=month)
        .values("subcategoria__nome")
        .annotate(total=Sum("valor"))
        .order_by("-total", "subcategoria__nome")[:limit]
    )
