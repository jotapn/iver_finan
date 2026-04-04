from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cadastros.models import Banco, CategoriaDeSpesa, FormaPagamento, Setor, SubcategoriaDeSpesa
from despesas.models import Despesa
from faturamento.models import RegistroFaturamento
from .services import get_dashboard_context


class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="admin", password="123456")
        categoria = CategoriaDeSpesa.objects.create(nome="Despesas Operacionais")
        subcategoria = SubcategoriaDeSpesa.objects.create(nome="Energia", categoria=categoria)
        forma = FormaPagamento.objects.create(nome="PIX")
        banco = Banco.objects.create(nome="Banco do Brasil")
        Setor.objects.create(nome="BAR")

        RegistroFaturamento.objects.create(
            data=date.today(),
            valor_dinheiro=100,
            valor_pix=50,
            valor_credito=0,
            valor_debito=0,
            valor_fiado=0,
            valor_vale=0,
            faturamento_bar=100,
            faturamento_cozinha=50,
        )
        Despesa.objects.create(
            descricao="Conta de luz",
            categoria=categoria,
            subcategoria=subcategoria,
            valor=40,
            forma_pagamento=forma,
            banco=banco,
            mes_referencia=date.today().month,
            ano_referencia=date.today().year,
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_renders(self):
        self.client.login(username="admin", password="123456")
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "Painel Financeiro")

    def test_dashboard_uses_net_revenue_for_balance(self):
        context = get_dashboard_context()
        self.assertEqual(context["resumo_mes"]["faturamento_bruto"], 150)
        self.assertEqual(context["resumo_mes"]["despesas"], 40)
        self.assertEqual(context["resumo_mes"]["saldo"], 95)

# Create your tests here.
