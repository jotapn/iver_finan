from __future__ import annotations

from calendar import monthrange
from collections import defaultdict
from datetime import date
from decimal import Decimal

from django.db.models import Sum

from cadastros.models import SubcategoriaDeSpesa

from .models import Despesa, RecorrenciaDespesa


def expense_summary_by_category(year: int, month: int):
    items = (
        Despesa.objects.filter(ano_referencia=year, mes_referencia=month)
        .values("categoria__nome", "subcategoria__nome")
        .annotate(total=Sum("valor"))
        .order_by("categoria__nome", "subcategoria__nome")
    )
    grouped = []
    current_category = None
    current_group = None

    for item in items:
        category_name = item["categoria__nome"]
        if category_name != current_category:
            current_category = category_name
            current_group = {
                "categoria": category_name,
                "total": Decimal("0.00"),
                "subcategorias": [],
            }
            grouped.append(current_group)

        subtotal = item["total"] or Decimal("0.00")
        current_group["subcategorias"].append(
            {
                "subcategoria": item["subcategoria__nome"],
                "total": subtotal,
            }
        )
        current_group["total"] += subtotal

    return grouped


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


def month_label(month: int) -> str:
    return {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Marco",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro",
    }.get(month, str(month))


def expense_period_choices():
    return [
        (f"{ano:04d}-{mes:02d}", f"{month_label(mes)}/{ano}")
        for ano, mes in (
            Despesa.objects.values_list("ano_referencia", "mes_referencia")
            .distinct()
            .order_by("-ano_referencia", "-mes_referencia")
        )
    ]


def grouped_subcategory_options():
    grouped = defaultdict(list)
    items = (
        SubcategoriaDeSpesa.objects.values("id", "nome", "categoria_id")
        .order_by("categoria__nome", "nome")
    )
    for item in items:
        grouped[str(item["categoria_id"])].append({"id": str(item["id"]), "nome": item["nome"]})
    return dict(grouped)


def month_start(year: int, month: int) -> date:
    return date(year, month, 1)


def next_month(value: date) -> date:
    if value.month == 12:
        return date(value.year + 1, 1, 1)
    return date(value.year, value.month + 1, 1)


def iter_periods(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current = next_month(current)


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
    recurrence_ids = list(recurrences.values_list("id", flat=True))
    if not recurrence_ids:
        return

    existing_periods = {
        (recorrencia_id, ano_referencia, mes_referencia)
        for recorrencia_id, ano_referencia, mes_referencia in Despesa.objects.filter(
            recorrencia_id__in=recurrence_ids,
            ano_referencia__lte=target_period.year,
        ).values_list("recorrencia_id", "ano_referencia", "mes_referencia")
    }
    pending_expenses = []

    for recorrencia in recurrences:
        current_period = month_start(recorrencia.data_inicio.year, recorrencia.data_inicio.month)
        final_period = target_period

        if recorrencia.data_fim:
            recurrence_end = month_start(recorrencia.data_fim.year, recorrencia.data_fim.month)
            if recurrence_end < final_period:
                final_period = recurrence_end

        for period in iter_periods(current_period, final_period):
            period_key = (recorrencia.id, period.year, period.month)
            if period_key not in existing_periods:
                pending_expenses.append(
                    Despesa(
                        descricao=recorrencia.descricao,
                        categoria=recorrencia.categoria,
                        subcategoria=recorrencia.subcategoria,
                        valor=recorrencia.valor,
                        data_vencimento=build_due_date(period.year, period.month, recorrencia.dia_vencimento),
                        data_pagamento=None,
                        forma_pagamento=recorrencia.forma_pagamento,
                        banco=recorrencia.banco,
                        pago=False,
                        mes_referencia=period.month,
                        ano_referencia=period.year,
                        observacao=recorrencia.observacao,
                        recorrencia=recorrencia,
                    )
                )
                existing_periods.add(period_key)

    if pending_expenses:
        Despesa.objects.bulk_create(pending_expenses)
