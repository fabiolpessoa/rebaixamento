from pprint import pprint
from django.core.management.base import BaseCommand
from core.services.scraper import baixar_estado_campeonato


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        dados = baixar_estado_campeonato()

        jogos = dados["jogos"]

        print("Total de jogos:", len(jogos))
        print()

        primeiro_id = list(jogos.keys())[0]

        print("Primeiro ID:", primeiro_id)
        print()

        pprint(jogos[primeiro_id], width=120)