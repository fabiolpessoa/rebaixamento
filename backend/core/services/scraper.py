import json
import requests

URL = URL = "https://ge.globo.com/futebol/brasileirao-serie-a/simulador-do-brasileirao-2026/"


def baixar_html():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    resposta = requests.get(URL, headers=headers, timeout=30)
    resposta.raise_for_status()
    return resposta.text


def extrair_classificacao():
    html = baixar_html()

    inicio = html.find("const classificacao =")

    if inicio == -1:
        raise Exception("Classificação não encontrada.")

    # primeira chave {
    inicio = html.find("{", inicio)

    contador = 0

    for i in range(inicio, len(html)):
        if html[i] == "{":
            contador += 1
        elif html[i] == "}":
            contador -= 1

            if contador == 0:
                fim = i + 1
                break

    json_texto = html[inicio:fim]

    dados = json.loads(json_texto)

    return dados["classificacao"]

def extrair_jogos():
    html = baixar_html()

    inicio = html.find("const listaJogos =")

    if inicio == -1:
        raise Exception("Lista de jogos não encontrada.")

    # primeira abertura do array
    inicio = html.find("[", inicio)

    contador = 0

    for i in range(inicio, len(html)):
        if html[i] == "[":
            contador += 1
        elif html[i] == "]":
            contador -= 1

            if contador == 0:
                fim = i + 1
                break

    jogos = json.loads(html[inicio:fim])

    return jogos

URL_SIMULADOR = (
    "https://ge.globo.com/futebol/brasileirao-serie-a/"
    "simulador-do-brasileirao-2026/"
    "servico/"
)


def baixar_simulador():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    resposta = requests.get(URL_SIMULADOR, headers=headers, timeout=30)
    resposta.raise_for_status()

    return resposta.json()

def baixar_bundle():
    url = (
        "https://s3.glbimg.com/v1/AUTH_378ee63fe83141e69caddd838034e850/"
        "static/interativos/futebol/brasileirao-serie-a/especial/"
        "simulador-do-brasileirao-2026/bundle.app.js"
    )

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    resposta = requests.get(url, headers=headers, timeout=30)
    resposta.raise_for_status()

    return resposta.text



URL_API = (
    "https://api.gcn.ge.globo.com/api/simuladores/"
    "estado-campeonato/campeonato-brasileiro/"
    "campeonato-brasileiro-2026/"
)

def baixar_estado_campeonato():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    resposta = requests.get(URL_API, headers=headers, timeout=30)
    resposta.raise_for_status()

    return resposta.json()