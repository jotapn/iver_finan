from datetime import date

from django.test import TestCase

from cadastros.models import Banco, CategoriaDeSpesa, FormaPagamento, SubcategoriaDeSpesa

from .models import Despesa
from .services import create_or_update_recurrence, expense_summary_by_category, generate_recurring_expenses_until


class DespesaTests(TestCase):
    def setUp(self):
        self.categoria = CategoriaDeSpesa.objects.create(nome="Despesas Operacionais")
        self.subcategoria = SubcategoriaDeSpesa.objects.create(nome="Energia", categoria=self.categoria)
        self.forma = FormaPagamento.objects.create(nome="PIX")
        self.banco = Banco.objects.create(nome="Nubank")

    def test_summary_uses_reference_month(self):
        Despesa.objects.create(
            descricao="Luz",
            categoria=self.categoria,
            subcategoria=self.subcategoria,
            valor=100,
            data_pagamento=date(2025, 2, 5),
            forma_pagamento=self.forma,
            banco=self.banco,
            mes_referencia=1,
            ano_referencia=2025,
        )
        resumo = list(expense_summary_by_category(2025, 1))
        self.assertEqual(resumo[0]["total"], 100)

    def test_monthly_recurrence_generates_future_expenses_until_end_date(self):
        despesa = Despesa.objects.create(
            descricao="Internet",
            categoria=self.categoria,
            subcategoria=self.subcategoria,
            valor=150,
            data_vencimento=date(2025, 1, 10),
            forma_pagamento=self.forma,
            banco=self.banco,
            mes_referencia=1,
            ano_referencia=2025,
        )
        recorrencia = create_or_update_recurrence(
            despesa,
            recorrente=True,
            recorrencia_ativa=True,
            recorrencia_data_fim=date(2025, 3, 31),
        )

        generate_recurring_expenses_until(2025, 4)

        meses = list(
            Despesa.objects.filter(recorrencia=recorrencia)
            .order_by("ano_referencia", "mes_referencia")
            .values_list("ano_referencia", "mes_referencia")
        )
        self.assertEqual(meses, [(2025, 1), (2025, 2), (2025, 3)])

    def test_disabling_recurrence_stops_future_generation(self):
        despesa = Despesa.objects.create(
            descricao="Aluguel",
            categoria=self.categoria,
            subcategoria=self.subcategoria,
            valor=500,
            data_vencimento=date(2025, 1, 5),
            forma_pagamento=self.forma,
            banco=self.banco,
            mes_referencia=1,
            ano_referencia=2025,
        )
        recorrencia = create_or_update_recurrence(
            despesa,
            recorrente=True,
            recorrencia_ativa=True,
            recorrencia_data_fim=None,
        )
        recorrencia.ativa = False
        recorrencia.save(update_fields=["ativa"])

        generate_recurring_expenses_until(2025, 3)

        self.assertEqual(Despesa.objects.filter(recorrencia=recorrencia).count(), 1)
