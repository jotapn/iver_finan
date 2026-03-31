from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class PerfilAcesso(models.Model):
    nome = models.CharField("nome", max_length=120, unique=True)
    ver_dashboard = models.BooleanField("ver dashboard", default=True)
    ver_cadastros = models.BooleanField("ver cadastros", default=True)
    ver_faturamento = models.BooleanField("ver faturamento", default=True)
    ver_despesas = models.BooleanField("ver despesas", default=True)
    ver_folha = models.BooleanField("ver folha", default=True)
    ver_dre = models.BooleanField("ver dre", default=True)
    ver_usuarios = models.BooleanField("ver usuarios", default=False)
    ver_admin = models.BooleanField("ver admin", default=False)

    class Meta:
        verbose_name = "perfil de acesso"
        verbose_name_plural = "perfis de acesso"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Perfil(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil")
    perfil_acesso = models.ForeignKey(
        PerfilAcesso,
        verbose_name="perfil de acesso",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="usuarios",
    )
    nome_completo = models.CharField("nome completo", max_length=200, blank=True)
    telefone = models.CharField("telefone", max_length=30, blank=True)
    cargo = models.CharField("cargo", max_length=120, blank=True)
    observacao = models.TextField("observacao", blank=True)

    class Meta:
        verbose_name = "perfil"
        verbose_name_plural = "perfis"
        ordering = ["nome_completo", "user__username"]

    def __str__(self):
        return self.nome_completo or self.user.username


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_profile_for_user(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)
    else:
        Perfil.objects.get_or_create(user=instance)
