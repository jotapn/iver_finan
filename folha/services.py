from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.db.models import Q, Sum

from cadastros.models import Colaborador
from faturamento.services import monthly_summary

from .models import BeneficioColaborador, LancamentoColaborador, PeriodoFolha


def productivity_base_for_sector(setor_nome: str, resumo_mensal: dict) -> Decimal:
    setor_nome = (setor_nome or "").upper()
    if setor_nome == "BAR":
        return resumo_mensal["total_bar"]
    if setor_nome == "COZINHA":
        return resumo_mensal["total_cozinha"]
    return resumo_mensal["total_bruto"]


def sync_periodo(periodo: PeriodoFolha) -> PeriodoFolha:
    resumo = monthly_summary(periodo.ano, periodo.mes)
    periodo.faturamento_total = resumo["total_bruto"]
    periodo.save(update_fields=["faturamento_total"])

    colaboradores = Colaborador.objects.select_related("cargo", "cargo__setor").filter(
        data_admissao__lte=date(periodo.ano, periodo.mes, monthrange(periodo.ano, periodo.mes)[1]),
        ativo=True,
    ).filter(Q(data_demissao__isnull=True) | Q(data_demissao__gte=date(periodo.ano, periodo.mes, 1)))

    for colaborador in colaboradores:
        base = productivity_base_for_sector(colaborador.cargo.setor.nome, resumo)
        produtividade_total = (base * colaborador.cargo.comissao_percentual).quantize(Decimal("0.01"))
        produtividade_1 = (produtividade_total / Decimal("2")).quantize(Decimal("0.01"))
        produtividade_2 = produtividade_total - produtividade_1
        lancamento, _ = LancamentoColaborador.objects.get_or_create(
            periodo=periodo,
            colaborador=colaborador,
            defaults={"salario_bruto": Decimal("0.00")},
        )
        lancamento.produtividade_1_valor = produtividade_1
        lancamento.produtividade_2_valor = produtividade_2
        lancamento.save()
        BeneficioColaborador.objects.get_or_create(periodo=periodo, colaborador=colaborador)

    return periodo


def resumo_despesas_trabalhistas(periodo: PeriodoFolha):
    return periodo.despesas_trabalhistas.values("tipo").annotate(total=Sum("valor")).order_by("tipo")
