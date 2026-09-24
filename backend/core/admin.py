from django.contrib import admin
from .models import Time, Jogo


@admin.register(Time)
class TimeAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "pontos",
        "jogos",
        "vitorias",
        "empates",
        "derrotas",
    )


@admin.register(Jogo)
class JogoAdmin(admin.ModelAdmin):
    list_display = (
        "rodada",
        "mandante",
        "visitante",
        "gols_mandante",
        "gols_visitante",
        "amarelos",
        "vermelhos",
        "finalizado",
    )

    list_filter = ("rodada", "finalizado")
    search_fields = ("mandante__nome", "visitante__nome")
