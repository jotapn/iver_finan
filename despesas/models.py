from django.db import models

from cadastros.models import Banco, CategoriaDeSpesa, FormaPagamento, SubcategoriaDeSpesa


class RecorrenciaDespesa(models.Model):
    descricao = models.CharField("descricao", max_length=255)
    categoria = models.ForeignKey(
        CategoriaDeSpesa,
        verbose_name="categoria",
        on_delete=models.PROTECT,
        related_name="recorrencias_despesa",
    )
    subcategoria = models.ForeignKey(
        SubcategoriaDeSpesa,
        verbose_name="subcategoria",
        on_delete=models.PROTECT,
        related_name="recorrencias_despesa",
    )
    valor = models.DecimalField("valor", max_digits=10, decimal_places=2)
    forma_pagamento = models.ForeignKey(
        FormaPagamento,
        verbose_name="forma de pagamento",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="recorrencias_despesa",
    )
    banco = models.ForeignKey(
        Banco,
        verbose_name="banco",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="recorrencias_despesa",
    )
    observacao = models.TextField("observacao", blank=True)
    ativa = models.BooleanField("ativa", default=True)
    data_inicio = models.DateField("data de inicio")
    data_fim = models.DateField("data de termino", null=True, blank=True)
    dia_vencimento = models.PositiveSmallIntegerField("dia de vencimento", null=True, blank=True)

    class Meta:
        verbose_name = "recorrencia de despesa"
        verbose_name_plural = "recorrencias de despesa"
        ordering = ["-data_inicio", "descricao"]

    def __str__(self):
        return self.descricao


class Despesa(models.Model):
    class Origem(models.TextChoices):
        MANUAL = "MANUAL", "Manual"
        FOLHA = "FOLHA", "Folha"

    descricao = models.CharField("descricao", max_length=255)
    categoria = models.ForeignKey(
        CategoriaDeSpesa,
        verbose_name="categoria",
        on_delete=models.PROTECT,
        related_name="despesas",
    )
    subcategoria = models.ForeignKey(
        SubcategoriaDeSpesa,
        verbose_name="subcategoria",
        on_delete=models.PROTECT,
        related_name="despesas",
    )
    valor = models.DecimalField("valor", max_digits=10, decimal_places=2)
    data_vencimento = models.DateField("data de vencimento", null=True, blank=True)
    data_pagamento = models.DateField("data de pagamento", null=True, blank=True)
    forma_pagamento = models.ForeignKey(
        FormaPagamento,
        verbose_name="forma de pagamento",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="despesas",
    )
    banco = models.ForeignKey(
        Banco,
        verbose_name="banco",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="despesas",
    )
    pago = models.BooleanField("pago", default=False)
    mes_referencia = models.IntegerField("mes de referencia")
    ano_referencia = models.IntegerField("ano de referencia")
    observacao = models.TextField("observacao", blank=True)
    recorrencia = models.ForeignKey(
        RecorrenciaDespesa,
        verbose_name="recorrencia",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="despesas",
    )
    origem = models.CharField("origem", max_length=20, choices=Origem.choices, default=Origem.MANUAL)
    folha_tipo = models.CharField("tipo da folha", max_length=50, blank=True)

    class Meta:
        verbose_name = "despesa"
        verbose_name_plural = "despesas"
        ordering = ["-ano_referencia", "-mes_referencia", "descricao"]

    def __str__(self):
        return self.descricao
