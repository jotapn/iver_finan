from datetime import date
from decimal import Decimal

from django.test import TestCase

from .forms import RegistroFaturamentoForm
from .models import RegistroFaturamento
from .services import monthly_summary


class FaturamentoTests(TestCase):
    def test_total_property_and_summary(self):
        registro = RegistroFaturamento.objects.create(
            data=date(2025, 1, 10),
            quantidade_pessoas=4,
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
        self.assertEqual(resumo["total_pessoas"], 4)
        self.assertEqual(resumo["total_liquido"], Decimal("180.00"))
        self.assertEqual(resumo["taxa_servico"], Decimal("20.00"))
        self.assertEqual(resumo["ticket_medio_diario"], Decimal("50.00"))

    def test_ticket_medio_ignora_dias_sem_quantidade_pessoas(self):
        RegistroFaturamento.objects.create(
            data=date(2025, 2, 10),
            quantidade_pessoas=4,
            valor_dinheiro=100,
            valor_pix=50,
            valor_credito=25,
            valor_debito=25,
        )
        RegistroFaturamento.objects.create(
            data=date(2025, 2, 11),
            valor_dinheiro=300,
        )

        resumo = monthly_summary(2025, 2)
        self.assertEqual(resumo["total_bruto"], Decimal("500"))
        self.assertEqual(resumo["total_bruto_com_pessoas"], Decimal("200"))
        self.assertEqual(resumo["total_pessoas"], 4)
        self.assertEqual(resumo["ticket_medio_diario"], Decimal("50.00"))

    def test_categorias_nao_podem_ultrapassar_total_do_dia(self):
        form = RegistroFaturamentoForm(
            data={
                "data": "2025-03-10",
                "valor_dinheiro": "100.00",
                "valor_pix": "50.00",
                "valor_credito": "0.00",
                "valor_debito": "0.00",
                "valor_fiado": "0.00",
                "valor_vale": "0.00",
                "faturamento_bar": "100.00",
                "faturamento_cozinha": "30.00",
                "faturamento_produtos": "20.00",
                "faturamento_outros": "10.00",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("A soma de Bar, Cozinha, Produtos e Outros", form.non_field_errors()[0])

# Create your tests here.
