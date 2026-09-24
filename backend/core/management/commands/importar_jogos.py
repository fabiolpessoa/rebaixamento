from django.core.management.base import BaseCommand

from core.models import Time, Jogo
from core.services.scraper import baixar_estado_campeonato


class Command(BaseCommand):
    help = "Importa os 380 jogos do Brasileirão"

    def handle(self, *args, **kwargs):

        dados = baixar_estado_campeonato()
        jogos = dados["jogos"]

        total = 0

        for jogo in jogos.values():

            mandante = Time.objects.get(
                id_api=jogo["equipe_mandante"]["equipe_id"]
            )

            visitante = Time.objects.get(
                id_api=jogo["equipe_visitante"]["equipe_id"]
            )

            Jogo.objects.update_or_create(
                id_api=jogo["jogo_id"],
                defaults={
                    "rodada": jogo["rodada"],
                    "mandante": mandante,
                    "visitante": visitante,
                    "gols_mandante": jogo["placar_oficial_mandante"],
                    "gols_visitante": jogo["placar_oficial_visitante"],
                    "finalizado": jogo["is_finalizado"],
                    "amarelos": 0,
                    "vermelhos": 0,
                }
            )

            total += 1

        self.stdout.write(
            self.style.SUCCESS(f"{total} jogos importados!")
        )