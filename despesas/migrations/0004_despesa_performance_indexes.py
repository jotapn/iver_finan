from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("despesas", "0003_despesa_folha_tipo_despesa_origem"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="despesa",
            index=models.Index(fields=["ano_referencia", "mes_referencia"], name="despesas_anoref_mesref_idx"),
        ),
        migrations.AddIndex(
            model_name="despesa",
            index=models.Index(
                fields=["recorrencia", "ano_referencia", "mes_referencia"],
                name="despesas_recorrencia_periodo_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="despesa",
            index=models.Index(fields=["pago", "ano_referencia", "mes_referencia"], name="despesas_pago_periodo_idx"),
        ),
    ]
