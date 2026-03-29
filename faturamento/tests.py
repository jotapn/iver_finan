from datetime import date
from decimal import Decimal

from django.test import TestCase

from .models import RegistroFaturamento
from .services import monthly_summary


class FaturamentoTests(TestCase):
    def test_total_property_and_summary(self):
        registro = RegistroFaturamento.objects.create(
            data=date(2025, 1, 10),
            valor_dinheiro=100,
            valor_pix=50,
            valor_credito=25,
            valor_debito=25,
            valor_fiado=0,
            valor_vale=0,
            faturamento_bar=120,
            faturamento_cozinha=80,
        )
        self.assertEqual(registro.total, Decimal("200.00"))

        resumo = monthly_summary(2025, 1)
        self.assertEqual(resumo["total_bruto"], Decimal("200"))
        self.assertEqual(resumo["taxa_servico"], Decimal("20.00"))

# Create your tests here.
