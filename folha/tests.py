from datetime import date
from decimal import Decimal

from django.test import TestCase

from cadastros.models import Cargo, Colaborador, Setor
from faturamento.models import RegistroFaturamento

from .models import PeriodoFolha
from .services import sync_periodo


class FolhaServiceTests(TestCase):
    def test_sync_period_generates_launches_and_productivity(self):
        setor = Setor.objects.create(nome="BAR")
        cargo = Cargo.objects.create(nome="Bartender", setor=setor, comissao_percentual=Decimal("0.0300"))
        colaborador = Colaborador.objects.create(nome="João", cargo=cargo, data_admissao=date(2025, 1, 1))
        RegistroFaturamento.objects.create(
            data=date(2025, 1, 10),
            valor_dinheiro=1000,
            valor_pix=0,
            valor_credito=0,
            valor_debito=0,
            valor_fiado=0,
            valor_vale=0,
            faturamento_bar=1000,
            faturamento_cozinha=0,
        )
        periodo = PeriodoFolha.objects.create(mes=1, ano=2025)
        sync_periodo(periodo)

        lancamento = periodo.lancamentos.get(colaborador=colaborador)
        self.assertEqual(periodo.faturamento_total, Decimal("1000"))
        self.assertEqual(lancamento.produtividade_1_valor + lancamento.produtividade_2_valor, Decimal("30.00"))

# Create your tests here.
