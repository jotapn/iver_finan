from django.db import models


class Banco(models.Model):
    nome = models.CharField("nome", max_length=120, unique=True)

    class Meta:
        verbose_name = "banco"
        verbose_name_plural = "bancos"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Setor(models.Model):
    nome = models.CharField("nome", max_length=120, unique=True)

    class Meta:
        verbose_name = "setor"
        verbose_name_plural = "setores"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Cargo(models.Model):
    nome = models.CharField("nome", max_length=120)
    setor = models.ForeignKey(Setor, verbose_name="setor", on_delete=models.PROTECT, related_name="cargos")
    comissao_percentual = models.DecimalField("comissao percentual", max_digits=5, decimal_places=4, default=0)

    class Meta:
        verbose_name = "cargo"
        verbose_name_plural = "cargos"
        ordering = ["nome"]
        unique_together = [("nome", "setor")]

    def __str__(self):
        return f"{self.nome} - {self.setor.nome}"


class Colaborador(models.Model):
    nome = models.CharField("nome", max_length=150)
    cargo = models.ForeignKey(Cargo, verbose_name="cargo", on_delete=models.PROTECT, related_name="colaboradores")
    documento = models.CharField("documento", max_length=30, blank=True)
    telefone = models.CharField("telefone", max_length=30, blank=True)
    email = models.EmailField("email", blank=True)
    cep = models.CharField("cep", max_length=10, blank=True)
    endereco = models.CharField("endereco", max_length=255, blank=True)
    numero = models.CharField("numero", max_length=20, blank=True)
    complemento = models.CharField("complemento", max_length=120, blank=True)
    bairro = models.CharField("bairro", max_length=120, blank=True)
    cidade = models.CharField("cidade", max_length=120, blank=True)
    uf = models.CharField("uf", max_length=2, blank=True)
    ativo = models.BooleanField("ativo", default=True)
    data_admissao = models.DateField("data de admissao")
    data_demissao = models.DateField("data de demissao", null=True, blank=True)

    class Meta:
        verbose_name = "colaborador"
        verbose_name_plural = "colaboradores"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class FormaPagamento(models.Model):
    nome = models.CharField("nome", max_length=120, unique=True)

    class Meta:
        verbose_name = "forma de pagamento"
        verbose_name_plural = "formas de pagamento"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class CategoriaDeSpesa(models.Model):
    nome = models.CharField("nome", max_length=150, unique=True)

    class Meta:
        verbose_name = "categoria de despesa"
        verbose_name_plural = "categorias de despesa"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class SubcategoriaDeSpesa(models.Model):
    nome = models.CharField("nome", max_length=150)
    categoria = models.ForeignKey(
        CategoriaDeSpesa,
        verbose_name="categoria",
        on_delete=models.CASCADE,
        related_name="subcategorias",
    )

    class Meta:
        verbose_name = "subcategoria de despesa"
        verbose_name_plural = "subcategorias de despesa"
        ordering = ["categoria__nome", "nome"]
        unique_together = [("nome", "categoria")]

    def __str__(self):
        return f"{self.categoria.nome} - {self.nome}"
