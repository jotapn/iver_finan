from __future__ import annotations

from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.db.models import Sum

from .models import Despesa, RecorrenciaDespesa


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


def month_start(year: int, month: int) -> date:
    return date(year, month, 1)


def next_month(value: date) -> date:
    if value.month == 12:
        return date(value.year + 1, 1, 1)
    return date(value.year, value.month + 1, 1)


def build_due_date(year: int, month: int, due_day: int | None) -> date | None:
    if not due_day:
        return None
    last_day = monthrange(year, month)[1]
    return date(year, month, min(due_day, last_day))


def create_or_update_recurrence(
    despesa: Despesa,
    *,
    recorrente: bool,
    recorrencia_ativa: bool,
    recorrencia_data_fim: date | None,
) -> RecorrenciaDespesa | None:
    if not recorrente:
        if despesa.recorrencia:
            despesa.recorrencia.ativa = False
            if recorrencia_data_fim:
                despesa.recorrencia.data_fim = recorrencia_data_fim
            despesa.recorrencia.save(update_fields=["ativa", "data_fim"])
        return None

    referencia_inicial = month_start(despesa.ano_referencia, despesa.mes_referencia)
    recorrencia = despesa.recorrencia or RecorrenciaDespesa()
    recorrencia.descricao = despesa.descricao
    recorrencia.categoria = despesa.categoria
    recorrencia.subcategoria = despesa.subcategoria
    recorrencia.valor = despesa.valor
    recorrencia.forma_pagamento = despesa.forma_pagamento
    recorrencia.banco = despesa.banco
    recorrencia.observacao = despesa.observacao
    recorrencia.ativa = recorrencia_ativa
    recorrencia.data_inicio = referencia_inicial
    recorrencia.data_fim = recorrencia_data_fim
    recorrencia.dia_vencimento = despesa.data_vencimento.day if despesa.data_vencimento else None
    recorrencia.save()

    if despesa.recorrencia_id != recorrencia.id:
        despesa.recorrencia = recorrencia
        despesa.save(update_fields=["recorrencia"])

    return recorrencia


def generate_recurring_expenses_until(year: int, month: int) -> None:
    target_period = month_start(year, month)
    recurrences = RecorrenciaDespesa.objects.filter(ativa=True).select_related(
        "categoria",
        "subcategoria",
        "forma_pagamento",
        "banco",
    )

    for recorrencia in recurrences:
        current_period = month_start(recorrencia.data_inicio.year, recorrencia.data_inicio.month)
        final_period = target_period

        if recorrencia.data_fim:
            recurrence_end = month_start(recorrencia.data_fim.year, recorrencia.data_fim.month)
            if recurrence_end < final_period:
                final_period = recurrence_end

        while current_period <= final_period:
            exists = Despesa.objects.filter(
                recorrencia=recorrencia,
                ano_referencia=current_period.year,
                mes_referencia=current_period.month,
            ).exists()
            if not exists:
                Despesa.objects.create(
                    descricao=recorrencia.descricao,
                    categoria=recorrencia.categoria,
                    subcategoria=recorrencia.subcategoria,
                    valor=recorrencia.valor,
                    data_vencimento=build_due_date(current_period.year, current_period.month, recorrencia.dia_vencimento),
                    data_pagamento=None,
                    forma_pagamento=recorrencia.forma_pagamento,
                    banco=recorrencia.banco,
                    pago=False,
                    mes_referencia=current_period.month,
                    ano_referencia=current_period.year,
                    observacao=recorrencia.observacao,
                    recorrencia=recorrencia,
                )
            current_period = next_month(current_period)
