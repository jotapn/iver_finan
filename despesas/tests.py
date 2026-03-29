from datetime import date

from django.test import TestCase

from cadastros.models import Banco, CategoriaDeSpesa, FormaPagamento, SubcategoriaDeSpesa

from .models import Despesa
from .services import expense_summary_by_category


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

# Create your tests here.
