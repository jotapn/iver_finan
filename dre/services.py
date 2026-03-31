from decimal import Decimal

from django.db.models import Sum
from openpyxl import Workbook

from cadastros.models import CategoriaDeSpesa, SubcategoriaDeSpesa
from despesas.models import Despesa
from despesas.services import generate_recurring_expenses_until
from faturamento.services import monthly_summary


PESSOAL_LABELS = [
    "Pro-labore",
    "Salário Bruto",
    "INSS Empresa",
    "Folgas e Dobras",
    "Horas Extras",
    "FGTS",
    "Exames Admissionais e Demissionais",
    "Uniforme",
    "Convênios e Seguros de Vida",
    "Seguro de Vida Coletivo",
    "13º Salário (50%)",
    "Provisão 13º",
    "Férias (Provisão)",
    "Rescisão Trabalhista",
    "FGTS - Rescisão",
]


def _total_despesa_subcategoria(subcategoria: SubcategoriaDeSpesa | None, year: int, month: int) -> Decimal:
    if subcategoria is None:
        return Decimal("0.00")
    return (
        Despesa.objects.filter(subcategoria=subcategoria, ano_referencia=year, mes_referencia=month).aggregate(total=Sum("valor"))[
            "total"
        ]
        or Decimal("0.00")
    )


def build_dre(year: int) -> dict:
    generate_recurring_expenses_until(year, 12)
    months = list(range(1, 13))
    receita_bruta = {month: monthly_summary(year, month)["total_bruto"] for month in months}
    taxa_servico = {month: (receita_bruta[month] * Decimal("0.10")).quantize(Decimal("0.01")) for month in months}
    receita_liquida = {month: (receita_bruta[month] - taxa_servico[month]).quantize(Decimal("0.01")) for month in months}

    def category_lines(category_name: str):
        category = CategoriaDeSpesa.objects.filter(nome=category_name).first()
        if not category:
            return [], {month: Decimal("0.00") for month in months}
        lines = []
        totals = {month: Decimal("0.00") for month in months}
        for subcategoria in category.subcategorias.order_by("nome"):
            values = {month: _total_despesa_subcategoria(subcategoria, year, month) for month in months}
            for month in months:
                totals[month] += values[month]
            lines.append({"label": subcategoria.nome, "values": values, "total": sum(values.values(), start=Decimal("0.00"))})
        return lines, totals

    pessoal_category = CategoriaDeSpesa.objects.filter(nome="Despesas com colaboradores").first()
    pessoal_lines = []
    total_pessoal = {month: Decimal("0.00") for month in months}
    for label in PESSOAL_LABELS:
        subcategoria = pessoal_category.subcategorias.filter(nome=label).first() if pessoal_category else None
        values = {month: _total_despesa_subcategoria(subcategoria, year, month) for month in months}
        for month in months:
            total_pessoal[month] += values[month]
        pessoal_lines.append({"label": label, "values": values, "total": sum(values.values(), start=Decimal("0.00"))})

    cmv_lines, total_cmv = category_lines("Custo de Mercadoria")
    operacionais_lines, total_operacionais = category_lines("Despesas Operacionais")
    financeiras_lines, total_financeiras = category_lines("Despesas Financeiras")

    resultado_antes_ir = {}
    resultado_liquido = {}
    for month in months:
        resultado_antes_ir[month] = (
            receita_liquida[month] - total_pessoal[month] - total_cmv[month] - total_operacionais[month] - total_financeiras[month]
        )
        resultado_liquido[month] = resultado_antes_ir[month]

    return {
        "year": year,
        "months": months,
        "receita_bruta": receita_bruta,
        "taxa_servico": taxa_servico,
        "receita_liquida": receita_liquida,
        "pessoal_lines": pessoal_lines,
        "total_pessoal": total_pessoal,
        "cmv_lines": cmv_lines,
        "total_cmv": total_cmv,
        "operacionais_lines": operacionais_lines,
        "total_operacionais": total_operacionais,
        "financeiras_lines": financeiras_lines,
        "total_financeiras": total_financeiras,
        "resultado_antes_ir": resultado_antes_ir,
        "resultado_liquido": resultado_liquido,
    }


def annual_total(values: dict[int, Decimal]) -> Decimal:
    return sum(values.values(), start=Decimal("0.00"))


def export_dre_workbook(data: dict) -> Workbook:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = f"DRE {data['year']}"
    headers = ["Conta", "JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ", "TOTAL"]
    sheet.append(headers)

    def append_line(label: str, values: dict[int, Decimal]):
        row = [label]
        for month in data["months"]:
            row.append(float(values[month]))
        row.append(float(annual_total(values)))
        sheet.append(row)

    append_line("Faturamento Bruto", data["receita_bruta"])
    append_line("Taxa de Serviço 10%", data["taxa_servico"])
    append_line("Faturamento Líquido", data["receita_liquida"])
    for line in data["pessoal_lines"]:
        append_line(line["label"], line["values"])
    append_line("TOTAL DESPESAS COM PESSOAL", data["total_pessoal"])
    for line in data["cmv_lines"]:
        append_line(line["label"], line["values"])
    append_line("TOTAL CMV", data["total_cmv"])
    for line in data["operacionais_lines"]:
        append_line(line["label"], line["values"])
    append_line("TOTAL DESPESAS OPERACIONAIS", data["total_operacionais"])
    for line in data["financeiras_lines"]:
        append_line(line["label"], line["values"])
    append_line("TOTAL DESPESAS FINANCEIRAS", data["total_financeiras"])
    append_line("RESULTADO ANTES DO IR", data["resultado_antes_ir"])
    append_line("RESULTADO LÍQUIDO", data["resultado_liquido"])
    return workbook
