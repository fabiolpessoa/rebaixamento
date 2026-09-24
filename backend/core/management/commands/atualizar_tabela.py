from django.core.management.base import BaseCommand

from core.models import Time, Jogo


class Command(BaseCommand):
    help = "Calcula a classificação pelos jogos finalizados"

    def handle(self, *args, **kwargs):

        # Zera as estatísticas
        Time.objects.all().update(
            pontos=0,
            jogos=0,
            vitorias=0,
            empates=0,
            derrotas=0,
            gols_pro=0,
            gols_contra=0,
        )

        jogos = Jogo.objects.filter(finalizado=True)

        for jogo in jogos:

            mandante = jogo.mandante
            visitante = jogo.visitante

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

            mandante.save()
            visitante.save()

        self.stdout.write(
            self.style.SUCCESS("Classificação atualizada!")
        )