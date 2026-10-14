
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Time, Jogo


class Command(BaseCommand):
    help = "Calcula a classificação pelos jogos finalizados"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # Guarda a posição atual antes de recalcular a classificação
        times_atuais = sorted(
            Time.objects.all(),
            key=lambda t: (
                t.pontos,
                t.vitorias,
                t.saldo,
                t.gols_pro,
                -t.cartoes_vermelhos,
                -t.cartoes_amarelos,
            ),
            reverse=True,
        )

        for posicao, time in enumerate(times_atuais, start=1):
            time.posicao_anterior = posicao

        Time.objects.bulk_update(
            times_atuais,
            ["posicao_anterior"],
        )

        # Zera as estatísticas em uma única operação
        Time.objects.all().update(
            pontos=0,
            jogos=0,
            vitorias=0,
            empates=0,
            derrotas=0,
            gols_pro=0,
            gols_contra=0,
        )

        # Carrega os times em memória para evitar consultas repetidas
        times = {
            time.id: time
            for time in Time.objects.all()
        }

        jogos = (
            Jogo.objects
            .filter(finalizado=True)
            .select_related("mandante", "visitante")
        )

        for jogo in jogos:
            mandante = times[jogo.mandante_id]
            visitante = times[jogo.visitante_id]

            gm = jogo.gols_mandante
            gv = jogo.gols_visitante

            mandante.jogos += 1
            visitante.jogos += 1

            mandante.gols_pro += gm
            mandante.gols_contra += gv

            visitante.gols_pro += gv
            visitante.gols_contra += gm

            if gm > gv:
                mandante.vitorias += 1
                mandante.pontos += 3
                visitante.derrotas += 1

            elif gm < gv:
                visitante.vitorias += 1
                visitante.pontos += 3
                mandante.derrotas += 1

            else:
                mandante.empates += 1
                visitante.empates += 1
                mandante.pontos += 1
                visitante.pontos += 1

        # Grava as estatísticas de todos os times em lote
        Time.objects.bulk_update(
            times.values(),
            [
                "pontos",
                "jogos",
                "vitorias",
                "empates",
                "derrotas",
                "gols_pro",
                "gols_contra",
            ],
        )

        self.stdout.write(
            self.style.SUCCESS("Classificação atualizada!")
        )
