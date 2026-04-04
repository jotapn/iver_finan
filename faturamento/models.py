from decimal import Decimal

from django.db import models


class RegistroFaturamento(models.Model):
    data = models.DateField("data", unique=True)
    quantidade_pessoas = models.PositiveIntegerField("quantidade de pessoas", null=True, blank=True)
    valor_dinheiro = models.DecimalField("valor em dinheiro", max_digits=10, decimal_places=2, default=0)
    valor_pix = models.DecimalField("valor em pix", max_digits=10, decimal_places=2, default=0)
    valor_credito = models.DecimalField("valor em crédito", max_digits=10, decimal_places=2, default=0)
    valor_debito = models.DecimalField("valor em débito", max_digits=10, decimal_places=2, default=0)
    valor_fiado = models.DecimalField("valor fiado", max_digits=10, decimal_places=2, default=0)
    valor_vale = models.DecimalField("valor em vale", max_digits=10, decimal_places=2, default=0)
    faturamento_bar = models.DecimalField("faturamento bar", max_digits=10, decimal_places=2, default=0)
    faturamento_cozinha = models.DecimalField("faturamento cozinha", max_digits=10, decimal_places=2, default=0)
    faturamento_produtos = models.DecimalField("faturamento produtos", max_digits=10, decimal_places=2, default=0)
    faturamento_outros = models.DecimalField("faturamento outros", max_digits=10, decimal_places=2, default=0)
    observacao = models.TextField("observação", blank=True)

    class Meta:
        verbose_name = "registro de faturamento"
        verbose_name_plural = "registros de faturamento"
        ordering = ["-data"]

    def __str__(self):
        return f"Faturamento {self.data:%d/%m/%Y}"

    @property
    def total(self):
        return sum(
            [
                self.valor_dinheiro,
                self.valor_pix,
                self.valor_credito,
                self.valor_debito,
                self.valor_fiado,
                self.valor_vale,
            ],
            start=Decimal("0.00"),
        )

# Create your models here.
