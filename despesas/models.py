from django.db import models

from cadastros.models import Banco, CategoriaDeSpesa, FormaPagamento, SubcategoriaDeSpesa


class Despesa(models.Model):
    descricao = models.CharField("descrição", max_length=255)
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
    mes_referencia = models.IntegerField("mês de referência")
    ano_referencia = models.IntegerField("ano de referência")
    observacao = models.TextField("observação", blank=True)

    class Meta:
        verbose_name = "despesa"
        verbose_name_plural = "despesas"
        ordering = ["-ano_referencia", "-mes_referencia", "descricao"]

    def __str__(self):
        return self.descricao

# Create your models here.
