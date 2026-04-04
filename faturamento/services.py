from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db.models import DecimalField, ExpressionWrapper, F, IntegerField, Sum, Value
from django.db.models.functions import Coalesce

from .models import RegistroFaturamento

MONTH_ABBR_PT = {
    1: "JAN",
    2: "FEV",
    3: "MAR",
    4: "ABR",
    5: "MAI",
    6: "JUN",
    7: "JUL",
    8: "AGO",
    9: "SET",
    10: "OUT",
    11: "NOV",
    12: "DEZ",
}


def total_expression():
    return ExpressionWrapper(
        F("valor_dinheiro")
        + F("valor_pix")
        + F("valor_credito")
        + F("valor_debito")
        + F("valor_fiado")
        + F("valor_vale"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )


def _zero(value):
    return value or Decimal("0.00")


def monthly_summary(year: int, month: int) -> dict:
    queryset = RegistroFaturamento.objects.filter(data__year=year, data__month=month)
    queryset_com_pessoas = queryset.filter(quantidade_pessoas__isnull=False)
    aggregates = queryset.aggregate(
        total_bruto=Coalesce(Sum(total_expression()), Value(Decimal("0.00"))),
        total_bar=Coalesce(Sum("faturamento_bar"), Value(Decimal("0.00"))),
        total_cozinha=Coalesce(Sum("faturamento_cozinha"), Value(Decimal("0.00"))),
    )
    aggregates_pessoas = queryset_com_pessoas.aggregate(
        total_bruto_com_pessoas=Coalesce(Sum(total_expression()), Value(Decimal("0.00"))),
        total_pessoas=Coalesce(Sum("quantidade_pessoas"), Value(0), output_field=IntegerField()),
    )
    total_bruto = _zero(aggregates["total_bruto"])
    dias_trabalhados = queryset.count()
    media_dia = (total_bruto / dias_trabalhados).quantize(Decimal("0.01")) if dias_trabalhados else Decimal("0.00")
    total_pessoas = aggregates_pessoas["total_pessoas"] or 0
    total_bruto_com_pessoas = _zero(aggregates_pessoas["total_bruto_com_pessoas"])
    ticket_medio_diario = (total_bruto_com_pessoas / total_pessoas).quantize(Decimal("0.01")) if total_pessoas else Decimal("0.00")
    return {
        "total_bruto": total_bruto,
        "dias_trabalhados": dias_trabalhados,
        "media_dia": media_dia,
        "total_pessoas": total_pessoas,
        "total_bruto_com_pessoas": total_bruto_com_pessoas,
        "ticket_medio_diario": ticket_medio_diario,
        "total_bar": _zero(aggregates["total_bar"]),
        "total_cozinha": _zero(aggregates["total_cozinha"]),
    }


def rolling_month_chart(reference_date: date, months: int = 6) -> dict:
    from despesas.models import Despesa

    labels = []
    faturamento = []
    despesas = []
    year = reference_date.year
    month = reference_date.month
    pairs = []
    for _ in range(months):
        pairs.append((year, month))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    pairs.reverse()

    for year, month in pairs:
        labels.append(f"{MONTH_ABBR_PT[month]}/{str(year)[-2:]}")
        resumo = monthly_summary(year, month)
        faturamento.append(float(resumo["total_bruto"]))
        total_despesas = _zero(
            Despesa.objects.filter(ano_referencia=year, mes_referencia=month).aggregate(total=Sum("valor"))["total"]
        )
        despesas.append(float(total_despesas))
    return {"labels": labels, "faturamento": faturamento, "despesas": despesas}
