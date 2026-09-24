from django.core.management.base import BaseCommand

from core.models import Time
from core.services.scraper import baixar_estado_campeonato


class Command(BaseCommand):
    help = "Importa os times do Brasileirão"

    def handle(self, *args, **kwargs):

        dados = baixar_estado_campeonato()

        equipes = dados["equipes"]

        total = 0

        for _, equipe in equipes.items():

            Time.objects.update_or_create(
                id_api=equipe["equipe_id"],
                defaults={
                    "nome": equipe["nome_popular"],
                    "sigla": equipe["sigla"],
                    "escudo": equipe["escudo"]["svg"],
                }
            )

            total += 1

        self.stdout.write(
            self.style.SUCCESS(f"{total} times importados!")
        )