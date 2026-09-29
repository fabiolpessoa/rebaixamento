from django.shortcuts import render
from core.models import Time
from core.services.rebaixamento import classificar_times, jogos_do_time



def dashboard(request):
    corte = int(request.GET.get("corte", 45))

    tabela = classificar_times(
        Time.objects.all(),
        corte=corte
    )

    jogos = {}

    for linha in tabela:
        jogos[linha.time.id] = jogos_do_time(linha.time)

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
