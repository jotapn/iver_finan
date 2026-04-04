from datetime import date
from decimal import Decimal

from django.test import TestCase

from cadastros.models import Cargo, Colaborador, Setor
from despesas.models import Despesa
from faturamento.models import RegistroFaturamento

from .models import BeneficioColaborador, PeriodoFolha
from .services import sync_periodo, sync_periodo_payment_expenses


class FolhaServiceTests(TestCase):
    def test_sync_period_generates_launches_without_automatic_productivity(self):
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
        self.assertEqual(lancamento.produtividade_1_valor, Decimal("0.00"))
        self.assertEqual(lancamento.produtividade_2_valor, Decimal("0.00"))

    def test_lancamento_calculates_fixed_split_and_manual_discounts(self):
        setor = Setor.objects.create(nome="SALAO")
        cargo = Cargo.objects.create(nome="Garcom", setor=setor, comissao_percentual=Decimal("0.0000"))
        colaborador = Colaborador.objects.create(
            nome="Carlos",
            cargo=cargo,
            salario_bruto=Decimal("1000.00"),
            data_admissao=date(2025, 1, 1),
        )
        periodo = PeriodoFolha.objects.create(mes=2, ano=2025)
        sync_periodo(periodo)

        lancamento = periodo.lancamentos.get(colaborador=colaborador)
        beneficio = BeneficioColaborador.objects.get(periodo=periodo, colaborador=colaborador)
        beneficio.ajuda_custo = Decimal("220.00")
        beneficio.vale_transporte = Decimal("176.00")
        beneficio.save()

        lancamento.consumo_colaborador = Decimal("50.00")
        lancamento.descontos = Decimal("50.00")
        lancamento.produtividade_1_valor = Decimal("100.00")
        lancamento.produtividade_2_valor = Decimal("80.00")
        lancamento.save()
        lancamento.beneficio = beneficio

        self.assertEqual(lancamento.adiantamento_valor, Decimal("400.00"))
        self.assertEqual(lancamento.saldo_salario_base, Decimal("600.00"))
        self.assertEqual(lancamento.saldo_final_sugerido, Decimal("500.00"))
        self.assertEqual(lancamento.saldo_final_valor, Decimal("500.00"))
        self.assertEqual(lancamento.total_beneficios, Decimal("396.00"))
        self.assertEqual(lancamento.total_recebido, Decimal("1476.00"))

    def test_paid_launches_generate_consolidated_expense(self):
        setor = Setor.objects.create(nome="COZINHA")
        cargo = Cargo.objects.create(nome="Cozinheiro", setor=setor, comissao_percentual=Decimal("0.0000"))
        colaborador = Colaborador.objects.create(
            nome="Maria",
            cargo=cargo,
            salario_bruto=Decimal("1000.00"),
            data_admissao=date(2025, 1, 1),
        )
        periodo = PeriodoFolha.objects.create(mes=3, ano=2025)
        sync_periodo(periodo)

        lancamento = periodo.lancamentos.get(colaborador=colaborador)
        lancamento.adiantamento_pago = True
        lancamento.adiantamento_data = date(2025, 3, 15)
        lancamento.save(update_fields=["adiantamento_pago", "adiantamento_data"])

        sync_periodo_payment_expenses(periodo)

        despesa = Despesa.objects.get(origem=Despesa.Origem.FOLHA, folha_tipo="ADIANTAMENTO", ano_referencia=2025, mes_referencia=3)
        self.assertEqual(despesa.valor, lancamento.adiantamento_valor)
        self.assertTrue(despesa.pago)
        self.assertEqual(despesa.subcategoria.nome, "Folha Adiantamento")

    def test_unpaid_launches_remove_consolidated_expense(self):
        setor = Setor.objects.create(nome="ATENDIMENTO")
        cargo = Cargo.objects.create(nome="Atendente", setor=setor, comissao_percentual=Decimal("0.0000"))
        colaborador = Colaborador.objects.create(
            nome="Paula",
            cargo=cargo,
            salario_bruto=Decimal("1000.00"),
            data_admissao=date(2025, 1, 1),
        )
        periodo = PeriodoFolha.objects.create(mes=4, ano=2025)
        sync_periodo(periodo)

        lancamento = periodo.lancamentos.get(colaborador=colaborador)
        lancamento.adiantamento_pago = True
        lancamento.adiantamento_data = date(2025, 4, 15)
        lancamento.save(update_fields=["adiantamento_pago", "adiantamento_data"])
        sync_periodo_payment_expenses(periodo)

        lancamento.adiantamento_pago = False
        lancamento.adiantamento_data = None
        lancamento.save(update_fields=["adiantamento_pago", "adiantamento_data"])
        sync_periodo_payment_expenses(periodo)

        self.assertFalse(
            Despesa.objects.filter(origem=Despesa.Origem.FOLHA, folha_tipo="ADIANTAMENTO", ano_referencia=2025, mes_referencia=4).exists()
        )

# Create your tests here.
