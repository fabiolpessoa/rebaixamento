
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Time, Jogo
from core.services.scraper import baixar_estado_campeonato


class Command(BaseCommand):
    help = "Importa os 380 jogos do Brasileirão"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        dados = baixar_estado_campeonato()
        jogos_api = dados["jogos"]

        times = {
            time.id_api: time
            for time in Time.objects.all()
        }

        jogos_existentes = {
            jogo.id_api: jogo
            for jogo in Jogo.objects.all()
            if jogo.id_api is not None
        }

        novos = []
        atualizados = []

        for dados_jogo in jogos_api.values():
            mandante_id = dados_jogo["equipe_mandante"]["equipe_id"]
            visitante_id = dados_jogo["equipe_visitante"]["equipe_id"]

            mandante = times.get(mandante_id)
            visitante = times.get(visitante_id)

            if mandante is None or visitante is None:
                raise ValueError(
                    f"Time não encontrado: mandante={mandante_id}, "
                    f"visitante={visitante_id}"
                )

            campos = {
                "rodada": dados_jogo["rodada"],
                "mandante": mandante,
                "visitante": visitante,
                "gols_mandante": dados_jogo["placar_oficial_mandante"],
                "gols_visitante": dados_jogo["placar_oficial_visitante"],
                "finalizado": dados_jogo["is_finalizado"],
                "amarelos": 0,
                "vermelhos": 0,
            }

            id_api = dados_jogo["jogo_id"]
            jogo_existente = jogos_existentes.get(id_api)

            if jogo_existente:
                for campo, valor in campos.items():
                    setattr(jogo_existente, campo, valor)
                atualizados.append(jogo_existente)
            else:
                novos.append(
                    Jogo(id_api=id_api, **campos)
                )

        if novos:
            Jogo.objects.bulk_create(novos, batch_size=100)

        if atualizados:
            Jogo.objects.bulk_update(
                atualizados,
                [
                    "rodada",
                    "mandante",
                    "visitante",
                    "gols_mandante",
                    "gols_visitante",
                    "finalizado",
                    "amarelos",
                    "vermelhos",
                ],
                batch_size=100,
            )

        total = len(novos) + len(atualizados)

        self.stdout.write(
            self.style.SUCCESS(
                f"{total} jogos importados! "
                f"Novos: {len(novos)}; atualizados: {len(atualizados)}."
            )
        )
