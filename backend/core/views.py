from django.shortcuts import render
from core.models import Time
from core.services.rebaixamento import classificar_times


def dashboard(request):
    corte = int(request.GET.get("corte", 45))

    tabela = classificar_times(
        Time.objects.all(),
        corte=corte
    )

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
        },
    )
