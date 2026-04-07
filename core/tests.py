from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cadastros.models import Banco, CategoriaDeSpesa, FormaPagamento, Setor, SubcategoriaDeSpesa
from despesas.models import Despesa
from faturamento.models import RegistroFaturamento
from .services import get_dashboard_context
from usuarios.models import PerfilAcesso
from usuarios.permissions import get_module_access_map


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

    def test_healthcheck_is_public(self):
        response = self.client.get(reverse("healthcheck"))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "ok"})

    def test_dashboard_renders(self):
        self.client.login(username="admin", password="123456")
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, "Painel Financeiro")

    def test_dashboard_uses_net_revenue_for_balance(self):
        context = get_dashboard_context()
        self.assertEqual(context["resumo_mes"]["faturamento_bruto"], 150)
        self.assertEqual(context["resumo_mes"]["despesas"], 40)
        self.assertEqual(context["resumo_mes"]["saldo"], 95)

    def test_module_access_map_is_cached_on_user(self):
        perfil_acesso = PerfilAcesso.objects.create(
            nome="Financeiro",
            ver_dashboard=True,
            ver_cadastros=False,
            ver_faturamento=True,
            ver_despesas=False,
            ver_folha=True,
            ver_dre=False,
            ver_usuarios=False,
            ver_admin=False,
        )
        self.user.perfil.perfil_acesso = perfil_acesso
        self.user.perfil.save(update_fields=["perfil_acesso"])

        access_map = get_module_access_map(self.user)

        self.assertIs(access_map, get_module_access_map(self.user))
        self.assertTrue(access_map["dashboard"])
        self.assertFalse(access_map["cadastros"])
        self.assertFalse(access_map["despesas"])
        self.assertTrue(access_map["folha"])

# Create your tests here.
