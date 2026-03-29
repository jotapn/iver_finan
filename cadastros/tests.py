from datetime import date

from django.test import TestCase

from .models import Banco, Cargo, CategoriaDeSpesa, Colaborador, Setor, SubcategoriaDeSpesa


class CadastroModelTests(TestCase):
    def test_str_methods(self):
        setor = Setor.objects.create(nome="BAR")
        cargo = Cargo.objects.create(nome="Bartender", setor=setor, comissao_percentual="0.0300")
        colaborador = Colaborador.objects.create(nome="Ana", cargo=cargo, data_admissao=date(2025, 1, 1))
        categoria = CategoriaDeSpesa.objects.create(nome="Operacionais")
        subcategoria = SubcategoriaDeSpesa.objects.create(nome="Energia", categoria=categoria)
        banco = Banco.objects.create(nome="Nubank")

        self.assertEqual(str(setor), "BAR")
        self.assertIn("Bartender", str(cargo))
        self.assertEqual(str(colaborador), "Ana")
        self.assertEqual(str(subcategoria), "Operacionais - Energia")
        self.assertEqual(str(banco), "Nubank")

# Create your tests here.
