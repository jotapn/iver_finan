from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.db.models import Max, Q, Sum

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

LANCAMENTO_RECALCULATED_FIELDS = [
    "salario_bruto",
    "inss",
    "adiantamento_valor",
    "saldo_final_valor",
    "salario_liquido",
    "adiantamento_data",
    "saldo_final_data",
    "produtividade_1_data",
    "produtividade_2_data",
]


def sync_periodo(periodo: PeriodoFolha) -> PeriodoFolha:
    resumo = monthly_summary(periodo.ano, periodo.mes)
    if periodo.faturamento_total != resumo["total_bruto"]:
        periodo.faturamento_total = resumo["total_bruto"]
        periodo.save(update_fields=["faturamento_total"])

    colaboradores = Colaborador.objects.select_related("cargo", "cargo__setor").filter(
        data_admissao__lte=date(periodo.ano, periodo.mes, monthrange(periodo.ano, periodo.mes)[1]),
        ativo=True,
    ).filter(Q(data_demissao__isnull=True) | Q(data_demissao__gte=date(periodo.ano, periodo.mes, 1)))
    colaboradores = list(colaboradores)

    existing_lancamentos = {
        lancamento.colaborador_id: lancamento
        for lancamento in LancamentoColaborador.objects.filter(periodo=periodo).select_related("colaborador")
    }
    existing_beneficios_ids = set(
        BeneficioColaborador.objects.filter(periodo=periodo).values_list("colaborador_id", flat=True)
    )

    missing_lancamentos = []
    lancamentos_to_update = []
    missing_beneficios = []

    for colaborador in colaboradores:
        lancamento = existing_lancamentos.get(colaborador.id)
        if lancamento is None:
            novo_lancamento = LancamentoColaborador(
                periodo=periodo,
                colaborador=colaborador,
                salario_bruto=colaborador.salario_bruto,
            )
            novo_lancamento.recalculate()
            missing_lancamentos.append(novo_lancamento)
        elif lancamento.salario_bruto != colaborador.salario_bruto:
            lancamento.salario_bruto = colaborador.salario_bruto
            lancamento.recalculate()
            lancamentos_to_update.append(lancamento)

        if colaborador.id not in existing_beneficios_ids:
            missing_beneficios.append(BeneficioColaborador(periodo=periodo, colaborador=colaborador))

    if missing_lancamentos:
        LancamentoColaborador.objects.bulk_create(missing_lancamentos)
    if lancamentos_to_update:
        LancamentoColaborador.objects.bulk_update(lancamentos_to_update, LANCAMENTO_RECALCULATED_FIELDS)
    if missing_beneficios:
        BeneficioColaborador.objects.bulk_create(missing_beneficios)

    sync_periodo_payment_expenses(periodo)
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
    lancamentos_summary = lancamentos.aggregate(
        adiantamento_total=Sum("adiantamento_valor", filter=Q(adiantamento_pago=True)),
        adiantamento_data=Max("adiantamento_data", filter=Q(adiantamento_pago=True)),
        saldo_final_total=Sum("saldo_final_valor", filter=Q(saldo_final_pago=True)),
        saldo_final_data=Max("saldo_final_data", filter=Q(saldo_final_pago=True)),
        produtividade_1_total=Sum("produtividade_1_valor", filter=Q(produtividade_1_pago=True)),
        produtividade_1_data=Max("produtividade_1_data", filter=Q(produtividade_1_pago=True)),
        produtividade_2_total=Sum("produtividade_2_valor", filter=Q(produtividade_2_pago=True)),
        produtividade_2_data=Max("produtividade_2_data", filter=Q(produtividade_2_pago=True)),
    )
    beneficios_summary = beneficios.aggregate(
        ajuda_custo_total=Sum("ajuda_custo", filter=Q(pago=True)),
        vale_transporte_total=Sum("vale_transporte", filter=Q(pago=True)),
        data_pagamento=Max("data_pagamento", filter=Q(pago=True)),
    )

    _sync_single_folha_expense(
        periodo=periodo,
        tipo="ADIANTAMENTO",
        valor=lancamentos_summary["adiantamento_total"],
        data_pagamento=lancamentos_summary["adiantamento_data"],
    )
    _sync_single_folha_expense(
        periodo=periodo,
        tipo="SALDO_FINAL",
        valor=lancamentos_summary["saldo_final_total"],
        data_pagamento=lancamentos_summary["saldo_final_data"],
    )
    _sync_single_folha_expense(
        periodo=periodo,
        tipo="PRODUTIVIDADE_1",
        valor=lancamentos_summary["produtividade_1_total"],
        data_pagamento=lancamentos_summary["produtividade_1_data"],
    )
    _sync_single_folha_expense(
        periodo=periodo,
        tipo="PRODUTIVIDADE_2",
        valor=lancamentos_summary["produtividade_2_total"],
        data_pagamento=lancamentos_summary["produtividade_2_data"],
    )
    _sync_single_folha_expense(
        periodo=periodo,
        tipo="AJUDA_CUSTO",
        valor=beneficios_summary["ajuda_custo_total"],
        data_pagamento=beneficios_summary["data_pagamento"],
    )
    _sync_single_folha_expense(
        periodo=periodo,
        tipo="VALE_TRANSPORTE",
        valor=beneficios_summary["vale_transporte_total"],
        data_pagamento=beneficios_summary["data_pagamento"],
    )
