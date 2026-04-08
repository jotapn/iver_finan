from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from despesas.models import Despesa
from despesas.services import generate_recurring_expenses_until
from faturamento.services import monthly_summary, rolling_month_chart
from folha.models import BeneficioColaborador, PeriodoFolha


def _zero(value: Decimal | None) -> Decimal:
    return value or Decimal("0.00")


def get_pending_payments_for_period(periodo: PeriodoFolha) -> list[dict]:
    pendencias = []

    for lancamento in periodo.lancamentos.select_related("colaborador"):
        if not lancamento.adiantamento_pago and lancamento.adiantamento_valor > 0:
            pendencias.append({"periodo": str(periodo), "ano": periodo.ano, "mes": periodo.mes, "colaborador": lancamento.colaborador.nome, "tipo": "Adiantamento"})
        if not lancamento.saldo_final_pago and lancamento.saldo_final_valor > 0:
            pendencias.append({"periodo": str(periodo), "ano": periodo.ano, "mes": periodo.mes, "colaborador": lancamento.colaborador.nome, "tipo": "Saldo final"})
        if not lancamento.produtividade_1_pago and lancamento.produtividade_1_valor > 0:
            pendencias.append({"periodo": str(periodo), "ano": periodo.ano, "mes": periodo.mes, "colaborador": lancamento.colaborador.nome, "tipo": "Produtividade 1"})
        if not lancamento.produtividade_2_pago and lancamento.produtividade_2_valor > 0:
            pendencias.append({"periodo": str(periodo), "ano": periodo.ano, "mes": periodo.mes, "colaborador": lancamento.colaborador.nome, "tipo": "Produtividade 2"})

    beneficios = BeneficioColaborador.objects.filter(periodo=periodo, pago=False).select_related("colaborador")
    for beneficio in beneficios:
        if (beneficio.vale_transporte or Decimal("0")) > 0:
            pendencias.append({"periodo": str(periodo), "ano": periodo.ano, "mes": periodo.mes, "colaborador": beneficio.colaborador.nome, "tipo": "Vale transporte"})
        if (beneficio.ajuda_custo or Decimal("0")) > 0:
            pendencias.append({"periodo": str(periodo), "ano": periodo.ano, "mes": periodo.mes, "colaborador": beneficio.colaborador.nome, "tipo": "Ajuda de custo"})

    return pendencias


def get_all_pending_payments() -> tuple[list[dict], list[str]]:
    pendencias = []
    periodos_com_pendencia = []

    for periodo in PeriodoFolha.objects.all():
        pendencias_periodo = get_pending_payments_for_period(periodo)
        if pendencias_periodo:
            periodos_com_pendencia.append(str(periodo))
            pendencias.extend(pendencias_periodo)

    return pendencias, periodos_com_pendencia


def get_dashboard_context() -> dict:
    today = timezone.localdate()
    pendencias_folha, periodos_folha_pendentes = get_all_pending_payments()
    generate_recurring_expenses_until(today.year, today.month)
    resumo_faturamento = monthly_summary(today.year, today.month)
    total_despesas = _zero(
        Despesa.objects.filter(ano_referencia=today.year, mes_referencia=today.month).aggregate(total=Sum("valor"))["total"]
    )
    folha_total = Decimal("0.00")
    periodo = PeriodoFolha.objects.filter(ano=today.year, mes=today.month).first()
    if periodo:
        folha_total = _zero(periodo.lancamentos.aggregate(total=Sum("salario_bruto"))["total"])
        folha_total += _zero(periodo.beneficios.aggregate(total=Sum("vale_transporte"))["total"])
        folha_total += _zero(periodo.beneficios.aggregate(total=Sum("ajuda_custo"))["total"])
        folha_total += _zero(
            Despesa.objects.filter(
                ano_referencia=today.year,
                mes_referencia=today.month,
                categoria__nome="Despesas com colaboradores",
            ).aggregate(total=Sum("valor"))["total"]
        )

    saldo = resumo_faturamento["total_liquido"] - total_despesas
    proximos_7 = today + timedelta(days=7)
    despesas_vencer = Despesa.objects.filter(
        pago=False,
        data_vencimento__isnull=False,
        data_vencimento__range=(today, proximos_7),
    ).select_related("categoria", "subcategoria")[:10]

    return {
        "resumo_mes": {
            "faturamento_bruto": resumo_faturamento["total_bruto"],
            "despesas": total_despesas,
            "saldo": saldo,
            "folha": folha_total,
        },
        "periodo_folha_referencia": date(today.year, today.month, 1),
        "periodos_folha_pendentes": periodos_folha_pendentes,
        "chart_data": rolling_month_chart(today, months=6),
        "despesas_vencer": despesas_vencer,
        "pendencias_folha": pendencias_folha,
    }
