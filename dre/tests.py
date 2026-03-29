from datetime import date
from decimal import Decimal

from django.test import TestCase

from cadastros.models import CategoriaDeSpesa, SubcategoriaDeSpesa
from despesas.models import Despesa
from faturamento.models import RegistroFaturamento
from folha.models import DespesaTrabalhistaMensal, PeriodoFolha

from .services import annual_total, build_dre


class DRETests(TestCase):
    def test_build_dre_aggregates_data(self):
        RegistroFaturamento.objects.create(
            data=date(2025, 1, 10),
            valor_dinheiro=1000,
            valor_pix=0,
            valor_credito=0,
            valor_debito=0,
            valor_fiado=0,
            valor_vale=0,
            faturamento_bar=500,
            faturamento_cozinha=500,
        )
        categoria = CategoriaDeSpesa.objects.create(nome="Despesas Operacionais")
        subcategoria = SubcategoriaDeSpesa.objects.create(nome="Energia", categoria=categoria)
        Despesa.objects.create(
            descricao="Conta de energia",
            categoria=categoria,
            subcategoria=subcategoria,
            valor=100,
            mes_referencia=1,
            ano_referencia=2025,
        )
        periodo = PeriodoFolha.objects.create(mes=1, ano=2025)
        DespesaTrabalhistaMensal.objects.create(periodo=periodo, tipo="FGTS", valor=50)

        dre = build_dre(2025)
        self.assertEqual(dre["receita_bruta"][1], Decimal("1000"))
        self.assertEqual(dre["total_operacionais"][1], Decimal("100"))
        self.assertEqual(dre["total_pessoal"][1], Decimal("50"))
        self.assertEqual(annual_total(dre["resultado_liquido"]), dre["resultado_liquido"][1])

# Create your tests here.
