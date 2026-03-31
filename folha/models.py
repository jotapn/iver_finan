from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.db import models

from cadastros.models import Banco, Colaborador


class PeriodoFolha(models.Model):
    mes = models.IntegerField("mês")
    ano = models.IntegerField("ano")
    faturamento_total = models.DecimalField("faturamento total", max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "período de folha"
        verbose_name_plural = "períodos de folha"
        ordering = ["-ano", "-mes"]
        unique_together = [("mes", "ano")]

    def __str__(self):
        return f"{self.mes:02d}/{self.ano}"


class LancamentoColaborador(models.Model):
    periodo = models.ForeignKey(PeriodoFolha, verbose_name="período", on_delete=models.CASCADE, related_name="lancamentos")
    colaborador = models.ForeignKey(
        Colaborador,
        verbose_name="colaborador",
        on_delete=models.CASCADE,
        related_name="lancamentos_folha",
    )
    salario_bruto = models.DecimalField("salário bruto", max_digits=10, decimal_places=2, default=0)
    inss = models.DecimalField("INSS", max_digits=10, decimal_places=2, default=0)
    vale_consumo = models.DecimalField("vale consumo", max_digits=10, decimal_places=2, default=0)
    salario_liquido = models.DecimalField("salário líquido", max_digits=10, decimal_places=2, default=0)
    adicional_noturno = models.DecimalField("adicional noturno", max_digits=10, decimal_places=2, default=0)
    dsr = models.DecimalField("DSR", max_digits=10, decimal_places=2, default=0)
    adiantamento_valor = models.DecimalField("adiantamento", max_digits=10, decimal_places=2, default=0)
    adiantamento_data = models.DateField("data do adiantamento", null=True, blank=True)
    adiantamento_pago = models.BooleanField("adiantamento pago", default=False)
    saldo_final_valor = models.DecimalField("saldo final", max_digits=10, decimal_places=2, default=0)
    saldo_final_data = models.DateField("data do saldo final", null=True, blank=True)
    saldo_final_pago = models.BooleanField("saldo final pago", default=False)
    produtividade_1_valor = models.DecimalField("produtividade 1", max_digits=10, decimal_places=2, default=0)
    produtividade_1_data = models.DateField("data produtividade 1", null=True, blank=True)
    produtividade_1_pago = models.BooleanField("produtividade 1 paga", default=False)
    produtividade_2_valor = models.DecimalField("produtividade 2", max_digits=10, decimal_places=2, default=0)
    produtividade_2_data = models.DateField("data produtividade 2", null=True, blank=True)
    produtividade_2_pago = models.BooleanField("produtividade 2 paga", default=False)

    class Meta:
        verbose_name = "lançamento de colaborador"
        verbose_name_plural = "lançamentos de colaboradores"
        ordering = ["colaborador__nome"]
        unique_together = [("periodo", "colaborador")]

    def __str__(self):
        return f"{self.colaborador.nome} - {self.periodo}"

    @property
    def total_recebido(self):
        return sum(
            [
                self.adiantamento_valor,
                self.saldo_final_valor,
                self.produtividade_1_valor,
                self.produtividade_2_valor,
            ],
            start=Decimal("0.00"),
        )

    def recalculate(self):
        self.inss = (self.salario_bruto * Decimal("0.075")).quantize(Decimal("0.01"))
        self.salario_liquido = (self.salario_bruto - self.inss - self.vale_consumo).quantize(Decimal("0.01"))
        self.adiantamento_valor = (self.salario_bruto * Decimal("0.40")).quantize(Decimal("0.01"))
        if not self.adiantamento_data:
            self.adiantamento_data = date(self.periodo.ano, self.periodo.mes, 15)
        if not self.saldo_final_data:
            next_month = self.periodo.mes + 1
            next_year = self.periodo.ano
            if next_month == 13:
                next_month = 1
                next_year += 1
            self.saldo_final_data = date(next_year, next_month, 5)
        if not self.produtividade_1_data:
            self.produtividade_1_data = date(self.periodo.ano, self.periodo.mes, min(20, monthrange(self.periodo.ano, self.periodo.mes)[1]))
        if not self.produtividade_2_data:
            self.produtividade_2_data = date(self.periodo.ano, self.periodo.mes, monthrange(self.periodo.ano, self.periodo.mes)[1])

    def save(self, *args, **kwargs):
        self.recalculate()
        super().save(*args, **kwargs)


class BeneficioColaborador(models.Model):
    periodo = models.ForeignKey(PeriodoFolha, verbose_name="período", on_delete=models.CASCADE, related_name="beneficios")
    colaborador = models.ForeignKey(
        Colaborador,
        verbose_name="colaborador",
        on_delete=models.CASCADE,
        related_name="beneficios_folha",
    )
    vale_transporte = models.DecimalField("vale transporte", max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    ajuda_custo = models.DecimalField("ajuda de custo", max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    data_vencimento = models.DateField("data de vencimento", null=True, blank=True)
    data_pagamento = models.DateField("data de pagamento", null=True, blank=True)
    pago = models.BooleanField("pago", default=False)

    class Meta:
        verbose_name = "benefício de colaborador"
        verbose_name_plural = "benefícios de colaboradores"
        unique_together = [("periodo", "colaborador")]
        ordering = ["colaborador__nome"]

    def __str__(self):
        return f"Benefícios - {self.colaborador.nome} - {self.periodo}"


class DespesaTrabalhistaMensal(models.Model):
    class Tipo(models.TextChoices):
        FGTS = "FGTS", "FGTS"
        INSS_EMPRESA = "INSS_EMPRESA", "INSS Empresa"
        SEGURO_VIDA = "SEGURO_VIDA", "Seguro de Vida Coletivo"
        DECIMO_TERCEIRO_50 = "13_SALARIO_50", "13º Salário (50%)"
        PROVISAO_13 = "PROVISAO_13", "Provisão 13º"
        EXAMES = "EXAMES", "Exames Admissionais e Demissionais"
        UNIFORME = "UNIFORME", "Uniforme"
        FERIAS_PROVISAO = "FERIAS_PROVISAO", "Férias (Provisão)"
        RESCISAO = "RESCISAO", "Rescisão Trabalhista"
        FGTS_RESCISAO = "FGTS_RESCISAO", "FGTS - Rescisão"
        PRO_LABORE = "PRO_LABORE", "Pro-labore"
        SALARIO_BRUTO = "SALARIO_BRUTO", "Salário Bruto"
        CONVENIO_SEGURO = "CONVENIO_SEGURO", "Convênios e Seguros de Vida"
        FOLGAS_DOBRAS = "FOLGAS_DOBRAS", "Folgas e Dobras"
        HORAS_EXTRAS = "HORAS_EXTRAS", "Horas Extras"

    periodo = models.ForeignKey(
        PeriodoFolha,
        verbose_name="período",
        on_delete=models.CASCADE,
        related_name="despesas_trabalhistas",
    )
    tipo = models.CharField("tipo", max_length=30, choices=Tipo.choices)
    valor = models.DecimalField("valor", max_digits=10, decimal_places=2)
    data_vencimento = models.DateField("data de vencimento", null=True, blank=True)
    data_pagamento = models.DateField("data de pagamento", null=True, blank=True)
    banco = models.ForeignKey(
        Banco,
        verbose_name="banco",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="despesas_trabalhistas",
    )
    pago = models.BooleanField("pago", default=False)

    class Meta:
        verbose_name = "despesa trabalhista mensal"
        verbose_name_plural = "despesas trabalhistas mensais"
        ordering = ["tipo"]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.periodo}"

# Create your models here.
