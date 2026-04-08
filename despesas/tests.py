from datetime import date

from django.test import TestCase

from cadastros.models import Banco, CategoriaDeSpesa, FormaPagamento, SubcategoriaDeSpesa

from .models import Despesa
from .services import (
    create_or_update_recurrence,
    expense_period_choices,
    expense_summary_by_category,
    generate_recurring_expenses_until,
    grouped_subcategory_options,
)


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

    def test_generate_recurring_expenses_is_idempotent(self):
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
        generate_recurring_expenses_until(2025, 4)

        self.assertEqual(Despesa.objects.filter(recorrencia=recorrencia).count(), 3)

    def test_grouped_subcategory_options_uses_single_map(self):
        outra_categoria = CategoriaDeSpesa.objects.create(nome="Administrativo")
        outra_subcategoria = SubcategoriaDeSpesa.objects.create(nome="Telefone", categoria=outra_categoria)

        options = grouped_subcategory_options()

        self.assertEqual(options[str(self.categoria.id)][0]["nome"], self.subcategoria.nome)
        self.assertEqual(options[str(outra_categoria.id)][0]["nome"], outra_subcategoria.nome)

    def test_expense_period_choices_returns_sorted_periods(self):
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
        Despesa.objects.create(
            descricao="Agua",
            categoria=self.categoria,
            subcategoria=self.subcategoria,
            valor=120,
            data_pagamento=date(2025, 3, 5),
            forma_pagamento=self.forma,
            banco=self.banco,
            mes_referencia=2,
            ano_referencia=2025,
        )

        self.assertEqual(expense_period_choices()[:2], [("2025-02", "Fevereiro/2025"), ("2025-01", "Janeiro/2025")])
