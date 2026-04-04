from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.db.models import Q, Sum

from cadastros.models import CategoriaDeSpesa, SubcategoriaDeSpesa
from cadastros.models import Colaborador
from despesas.models import Despesa
from faturamento.services import monthly_summary

from .models import BeneficioColaborador, LancamentoColaborador, PeriodoFolha


FOLHA_DESPESA_CATEGORIA = "Despesa Trabalhista"
FOLHA_DESPESA_TIPOS = {
    "ADIANTAMENTO": "Folha Adiantamento",
    "SALDO_FINAL": "Folha Saldo Final",
    "PRODUTIVIDADE_1": "Folha Produtividade 1",
    "PRODUTIVIDADE_2": "Folha Produtividade 2",
    "AJUDA_CUSTO": "Folha Ajuda de Custo",
    "VALE_TRANSPORTE": "Folha Vale Transporte",
}


def sync_periodo(periodo: PeriodoFolha) -> PeriodoFolha:
    resumo = monthly_summary(periodo.ano, periodo.mes)
    periodo.faturamento_total = resumo["total_bruto"]
    periodo.save(update_fields=["faturamento_total"])

    colaboradores = Colaborador.objects.select_related("cargo", "cargo__setor").filter(
        data_admissao__lte=date(periodo.ano, periodo.mes, monthrange(periodo.ano, periodo.mes)[1]),
        ativo=True,
    ).filter(Q(data_demissao__isnull=True) | Q(data_demissao__gte=date(periodo.ano, periodo.mes, 1)))

    for colaborador in colaboradores:
        lancamento, _ = LancamentoColaborador.objects.get_or_create(
            periodo=periodo,
            colaborador=colaborador,
            defaults={"salario_bruto": colaborador.salario_bruto},
        )
        lancamento.salario_bruto = colaborador.salario_bruto
        lancamento.save()
        BeneficioColaborador.objects.get_or_create(periodo=periodo, colaborador=colaborador)

    return periodo


def _ensure_folha_expense_classification(tipo: str) -> tuple[CategoriaDeSpesa, SubcategoriaDeSpesa]:
    categoria, _ = CategoriaDeSpesa.objects.get_or_create(nome=FOLHA_DESPESA_CATEGORIA)
    subcategoria, _ = SubcategoriaDeSpesa.objects.get_or_create(
        categoria=categoria,
        nome=FOLHA_DESPESA_TIPOS[tipo],
    )
    return categoria, subcategoria


def _sync_single_folha_expense(
    *,
    periodo: PeriodoFolha,
    tipo: str,
    valor: Decimal | None,
    data_pagamento,
) -> None:
    valor = valor or Decimal("0.00")
    existing = Despesa.objects.filter(
        origem=Despesa.Origem.FOLHA,
        folha_tipo=tipo,
        ano_referencia=periodo.ano,
        mes_referencia=periodo.mes,
    )

    if valor <= 0:
        existing.delete()
        return

    categoria, subcategoria = _ensure_folha_expense_classification(tipo)
    defaults = {
        "descricao": f"{FOLHA_DESPESA_TIPOS[tipo]} {periodo}",
        "categoria": categoria,
        "subcategoria": subcategoria,
        "valor": valor,
        "data_vencimento": data_pagamento,
        "data_pagamento": data_pagamento,
        "pago": True,
        "observacao": f"Lancamento automatico gerado pela folha do periodo {periodo}.",
    }
    despesa, created = Despesa.objects.get_or_create(
        origem=Despesa.Origem.FOLHA,
        folha_tipo=tipo,
        ano_referencia=periodo.ano,
        mes_referencia=periodo.mes,
        defaults=defaults,
    )
    if not created:
        for field, field_value in defaults.items():
            setattr(despesa, field, field_value)
        despesa.save(
            update_fields=[
                "descricao",
                "categoria",
                "subcategoria",
                "valor",
                "data_vencimento",
                "data_pagamento",
                "pago",
                "observacao",
            ]
        )


def sync_periodo_payment_expenses(periodo: PeriodoFolha) -> None:
    lancamentos = periodo.lancamentos.all()
    beneficios = periodo.beneficios.all()

    _sync_single_folha_expense(
        periodo=periodo,
        tipo="ADIANTAMENTO",
        valor=lancamentos.filter(adiantamento_pago=True).aggregate(total=Sum("adiantamento_valor"))["total"],
        data_pagamento=lancamentos.filter(adiantamento_pago=True).order_by("-adiantamento_data").values_list("adiantamento_data", flat=True).first(),
    )
    _sync_single_folha_expense(
        periodo=periodo,
        tipo="SALDO_FINAL",
        valor=lancamentos.filter(saldo_final_pago=True).aggregate(total=Sum("saldo_final_valor"))["total"],
        data_pagamento=lancamentos.filter(saldo_final_pago=True).order_by("-saldo_final_data").values_list("saldo_final_data", flat=True).first(),
    )
    _sync_single_folha_expense(
        periodo=periodo,
        tipo="PRODUTIVIDADE_1",
        valor=lancamentos.filter(produtividade_1_pago=True).aggregate(total=Sum("produtividade_1_valor"))["total"],
        data_pagamento=lancamentos.filter(produtividade_1_pago=True).order_by("-produtividade_1_data").values_list("produtividade_1_data", flat=True).first(),
    )
    _sync_single_folha_expense(
        periodo=periodo,
        tipo="PRODUTIVIDADE_2",
        valor=lancamentos.filter(produtividade_2_pago=True).aggregate(total=Sum("produtividade_2_valor"))["total"],
        data_pagamento=lancamentos.filter(produtividade_2_pago=True).order_by("-produtividade_2_data").values_list("produtividade_2_data", flat=True).first(),
    )
    _sync_single_folha_expense(
        periodo=periodo,
        tipo="AJUDA_CUSTO",
        valor=beneficios.filter(pago=True).aggregate(total=Sum("ajuda_custo"))["total"],
        data_pagamento=beneficios.filter(pago=True).order_by("-data_pagamento").values_list("data_pagamento", flat=True).first(),
    )
    _sync_single_folha_expense(
        periodo=periodo,
        tipo="VALE_TRANSPORTE",
        valor=beneficios.filter(pago=True).aggregate(total=Sum("vale_transporte"))["total"],
        data_pagamento=beneficios.filter(pago=True).order_by("-data_pagamento").values_list("data_pagamento", flat=True).first(),
    )
