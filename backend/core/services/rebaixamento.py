from dataclasses import dataclass
from core.models import Time
from core.models import Jogo
from django.db.models import Q

RODADAS = 38


@dataclass
class LinhaTabela:
    time: Time
    posicao: int

    variacao_posicao: int

    jogos_restantes: int
    jogos_atrasados: bool

    camp_pct: float
    rec_pct: float
    nec_pct: float
    delta_pct: float
    pontos_faltantes: int | None

    criterio: str
    status: str

    jogos_anteriores: list
    jogos_proximos: list


def percentual(pontos, jogos):
    if jogos == 0:
        return 0.0
    return round((pontos / (jogos * 3)) * 100, 1)


def aproveitamento_necessario(time, corte):
    restantes = RODADAS - time.jogos

    if time.pontos >= corte:
        return 0.0

    if restantes == 0:
        return 100.0

    pontos_faltantes = corte - time.pontos
    return round((pontos_faltantes / (restantes * 3)) * 100, 1)


def definir_status(time, rec, nec, corte):
    restantes = 38 - time.jogos

    # Já está matematicamente salvo
    if time.pontos >= corte:
        return "AZUL"

    # Não consegue mais atingir a pontuação de corte
    if time.pontos + (restantes * 3) < corte:
        return "PRETO"

    delta = rec - nec

    if delta >= 15:
        return "VERDE"
    elif delta >= 5:
        return "AMARELO"
    else:
        return "VERMELHO"

def criterio_desempate(atual, anterior):
    """
    Retorna qual critério colocou 'atual' atrás de 'anterior'.
    """

    if atual.pontos != anterior.pontos:
        return ""

    if atual.vitorias != anterior.vitorias:
        return "V"

    saldo_atual = atual.gols_pro - atual.gols_contra
    saldo_ant = anterior.gols_pro - anterior.gols_contra

    if saldo_atual != saldo_ant:
        return "Δ"

    if atual.gols_pro != anterior.gols_pro:
        return "⚽"

    # Confronto direto será implementado depois
    if atual.cartoes_vermelhos != anterior.cartoes_vermelhos:
        return "🟥"

    if atual.cartoes_amarelos != anterior.cartoes_amarelos:
        return "🟨"

    return ""

def grupos_empate(times):
    grupos = []
    atual = []

    for time in times:
        if not atual:
            atual.append(time)
            continue

        if time.pontos == atual[0].pontos:
            atual.append(time)
        else:
            grupos.append(atual)
            atual = [time]

    if atual:
        grupos.append(atual)

    return grupos

def calcular_posicoes_anteriores(times):
    jogos_finalizados = Jogo.objects.filter(
        finalizado=True
    ).order_by("-rodada")

    if not jogos_finalizados.exists():
        return {time.id: None for time in times}

    ultima_rodada = jogos_finalizados.first().rodada

    jogos_ultima_rodada = Jogo.objects.filter(
        rodada=ultima_rodada,
        finalizado=True
    )

    dados = {}

    for time in times:
        dados[time.id] = {
            "pontos": time.pontos,
            "vitorias": time.vitorias,
            "saldo": time.saldo,
            "gols_pro": time.gols_pro,
            "vermelhos": time.cartoes_vermelhos,
            "amarelos": time.cartoes_amarelos,
        }

    for jogo in jogos_ultima_rodada:
        mandante = dados[jogo.mandante.id]
        visitante = dados[jogo.visitante.id]

        # Remove os gols do último jogo
        mandante["gols_pro"] -= jogo.gols_mandante
        mandante["saldo"] -= jogo.gols_mandante - jogo.gols_visitante

        visitante["gols_pro"] -= jogo.gols_visitante
        visitante["saldo"] -= jogo.gols_visitante - jogo.gols_mandante

        # Remove os pontos e a vitória conquistados na rodada
        if jogo.gols_mandante > jogo.gols_visitante:
            mandante["pontos"] -= 3
            mandante["vitorias"] -= 1

        elif jogo.gols_visitante > jogo.gols_mandante:
            visitante["pontos"] -= 3
            visitante["vitorias"] -= 1

        else:
            mandante["pontos"] -= 1
            visitante["pontos"] -= 1

    ordenados = sorted(
        times,
        key=lambda t: (
            dados[t.id]["pontos"],
            dados[t.id]["vitorias"],
            dados[t.id]["saldo"],
            dados[t.id]["gols_pro"],
            -dados[t.id]["vermelhos"],
            -dados[t.id]["amarelos"],
        ),
        reverse=True,
    )

    return {
        time.id: pos
        for pos, time in enumerate(ordenados, start=1)
    }

def classificar_times(times, corte=45):
    ordenados = sorted(
        times,
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

    rodada_atual = max(t.jogos for t in ordenados)
    posicoes_anteriores = calcular_posicoes_anteriores(ordenados)
    grupos = grupos_empate(ordenados)
    criterios = {}

    # Descobre qual critério decidiu cada grupo empatado
    for grupo in grupos:

        if len(grupo) == 1:
            criterios[grupo[0].id] = ""
            continue

        grupo_ordenado = sorted(
            grupo,
            key=lambda t: (
                t.vitorias,
                t.saldo,
                t.gols_pro,
                -t.cartoes_vermelhos,
                -t.cartoes_amarelos,
            ),
            reverse=True,
        )

        criterios[grupo_ordenado[0].id] = ""

        for i in range(1, len(grupo_ordenado)):
            anterior = grupo_ordenado[i - 1]
            atual = grupo_ordenado[i]
            criterios[atual.id] = criterio_desempate(atual, anterior)

    tabela = []

    for pos, time in enumerate(ordenados, start=1):

        variacao_posicao = posicoes_anteriores[time.id] - pos

        camp = percentual(time.pontos, time.jogos)

        rec = aproveitamento_recente(time)

        if time.pontos >= corte:
            nec = None
            delta = None
            pontos_faltantes = None
        else:
            nec = aproveitamento_necessario(time, corte)
            delta = round(rec - nec, 1)
            pontos_faltantes = corte - time.pontos

        if pos == 1:
            criterio = ""
        else:
            criterio = criterio_desempate(time, ordenados[pos - 2])

        atrasado = time.jogos < rodada_atual

        status = definir_status(time, rec, nec, corte)

        tabela.append(
            LinhaTabela(
                time=time,
                posicao=pos,
                variacao_posicao=variacao_posicao,
                jogos_restantes=RODADAS - time.jogos,
                jogos_atrasados=atrasado,
                camp_pct=camp,
                rec_pct=rec,
                nec_pct=nec,
                delta_pct=delta,
                pontos_faltantes=pontos_faltantes,
                criterio=criterio,
                status=status,
                jogos_anteriores=jogos_do_time(time)["anteriores"],
                jogos_proximos=jogos_do_time(time)["proximos"],
            )
        )

    return tabela


def aproveitamento_recente(time):
    restantes = 38 - time.jogos

    if restantes == 0:
        return 0.0

    jogos = (
        Jogo.objects
        .filter(finalizado=True)
        .filter(Q(mandante=time) | Q(visitante=time))
        .order_by("-rodada")[:restantes]
    )

    if not jogos:
        return 0.0

    pontos = 0

    for jogo in jogos:
        if jogo.mandante == time:
            pro = jogo.gols_mandante
            contra = jogo.gols_visitante
        else:
            pro = jogo.gols_visitante
            contra = jogo.gols_mandante

        if pro > contra:
            pontos += 3
        elif pro == contra:
            pontos += 1

    return round((pontos / (len(jogos) * 3)) * 100, 1)

def jogos_do_time(time):
    jogos = (
        Jogo.objects
        .filter(Q(mandante=time) | Q(visitante=time))
        .order_by("rodada")
    )

    jogos_anteriores = []
    jogos_proximos = []

    for jogo in jogos:
        if jogo.finalizado:
            jogos_anteriores.append(jogo)
        else:
            jogos_proximos.append(jogo)

    return {
        "anteriores": jogos_anteriores[-5:],
        "proximos": jogos_proximos[:5],
    }