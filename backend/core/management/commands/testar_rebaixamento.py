from django.core.management.base import BaseCommand
from core.models import Time
from core.services.rebaixamento import classificar_times


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        tabela = classificar_times(
            Time.objects.all(),
            rodada_atual=30,
            corte=45
        )

        for t in tabela:
            atraso = "⏰" if t.jogos_atrasados else ""

            print(
                f"{t.posicao:2}  "
                f"{t.time.nome:15} "
                f"{t.time.pontos:2}{atraso}  "
                f"Crit:{t.criterio:2}  "
                f"Camp:{t.camp_pct:5.1f}%  "
                f"Rec:{t.rec_pct:5.1f}%  "
                f"Nec:{t.nec_pct:5.1f}%  "
                f"Δ:{t.delta_pct:+5.1f}%  "
                f"{t.status}"
            )