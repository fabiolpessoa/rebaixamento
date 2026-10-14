from django.shortcuts import render
from core.models import Time, Jogo
from core.services.rebaixamento import classificar_times
from django.db.models import Q
from django.shortcuts import redirect
from django.core.management import call_command
from django.contrib import messages
from django.views.decorators.http import require_POST



def dashboard(request):
    corte = int(request.GET.get("corte", 45))

    tabela = classificar_times(
        Time.objects.all(),
        corte=corte
    )

    jogos = {linha.time.id: {"anteriores": [], "proximos": []} for linha in tabela}

    todos_jogos = (
        Jogo.objects
        .filter(
            Q(mandante__in=[linha.time for linha in tabela]) |
            Q(visitante__in=[linha.time for linha in tabela])
        )
        .select_related("mandante", "visitante")
        .order_by("rodada")
    )

    for jogo in todos_jogos:
        for time_id in (jogo.mandante_id, jogo.visitante_id):
            if time_id not in jogos:
                continue

            if jogo.finalizado:
                jogos[time_id]["anteriores"].append(jogo)
            else:
                jogos[time_id]["proximos"].append(jogo)

    for dados in jogos.values():
        dados["anteriores"] = dados["anteriores"][-5:]
        dados["proximos"] = dados["proximos"][:5]

    return render(
        request,
        "dashboard.html",
        {
            "tabela": tabela,
            "corte": corte,
            "salvos": sum(1 for t in tabela if t.status == "AZUL"),
            "verdes": sum(1 for t in tabela if t.status == "VERDE"),
            "amarelos": sum(1 for t in tabela if t.status == "AMARELO"),
            "vermelhos": sum(1 for t in tabela if t.status == "VERMELHO"),
            "pretos": sum(1 for t in tabela if t.status == "PRETO"),
            "jogos": jogos,
        },
    )

@require_POST
def atualizar_dados(request):
    try:
        call_command("importar_jogos")
        call_command("atualizar_tabela")
        messages.success(request, "Jogos importados e classificação atualizada!")
    except Exception as erro:
        messages.error(request, f"Erro ao atualizar os dados: {erro}")

    return redirect("dashboard")

