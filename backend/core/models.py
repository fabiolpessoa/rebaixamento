from django.db import models


class Time(models.Model):
    id_api = models.IntegerField(unique=True)

    nome = models.CharField(max_length=80)
    sigla = models.CharField(max_length=3)
    escudo = models.URLField()

    pontos = models.IntegerField(default=0)
    jogos = models.IntegerField(default=0)

    vitorias = models.IntegerField(default=0)
    empates = models.IntegerField(default=0)
    derrotas = models.IntegerField(default=0)

    gols_pro = models.IntegerField(default=0)
    gols_contra = models.IntegerField(default=0)

    cartoes_amarelos = models.IntegerField(default=0)
    cartoes_vermelhos = models.IntegerField(default=0)

    @property
    def saldo(self):
        return self.gols_pro - self.gols_contra

class Jogo(models.Model):
    #id_api = models.IntegerField(unique=True)
    id_api = models.IntegerField(
        unique=True,
        null=True,
        blank=True
        )   

    rodada = models.IntegerField()

    mandante = models.ForeignKey(
        Time,
        on_delete=models.CASCADE,
        related_name="jogos_mandante"
    )

    visitante = models.ForeignKey(
        Time,
        on_delete=models.CASCADE,
        related_name="jogos_visitante"
    )

    gols_mandante = models.IntegerField(null=True, blank=True)
    gols_visitante = models.IntegerField(null=True, blank=True)

    amarelos = models.IntegerField(default=0)
    vermelhos = models.IntegerField(default=0)

    finalizado = models.BooleanField(default=False)

    def __str__(self):
        return f"R{self.rodada} - {self.mandante} x {self.visitante}"