from bs4 import BeautifulSoup
from common import *

URL_BASE = "https://insulartc.com.br"
URL_LINHAS = URL_BASE + "/est/wp/"


def raspar_linhas() -> list[Linha]:
    html, _ = get_html(URL_LINHAS)
    soup = BeautifulSoup(html, "html.parser")
    linhas: list[Linha] = []

    for tr in soup.find_all("tr"):
        tag_cod = tr.select_one(":first-child")
        tag_nome = tr.select_one("a")

        if tag_cod is None or tag_nome is None:
            continue

        codigo = extrair_texto(tag_cod)
        nome = extrair_texto(tag_nome)

        executivo = "executivo" in nome.lower() or "VIP" in nome
        url = str(tag_nome["href"])

        linhas.append(Linha(codigo, nome, "", executivo, url))

    return linhas


DIAS = ["UTIL", "UTIL", "UTIL", "SABADO", "SABADO", "DOMINGO_FERIADO"]


def raspar_horarios_linha(linha: Linha) -> list[Horario]:
    soup = BeautifulSoup(linha.url, "html.parser")
    horarios: list[Horario] = []

    sentido = ""
    for tr in soup.find_all("tr"):
        colunas = tr.find_all("td")

        if len(colunas) == 3:
            texto = extrair_texto(colunas[1])
            if "(Ida)" in texto or "(Volta)" in texto or "Partida" in texto:
                sentido = texto
            continue

        if len(colunas) != 8 or sentido == "":
            continue

        for i, dia in enumerate(DIAS):
            hora = extrair_texto(colunas[i + 1])

            if len(hora) == 0:
                continue

            match_limpo = re.findall("([0-9]+:[0-9]+)", hora.replace(".", ":"))

            if len(match_limpo) == 0:
                continue

            hora = match_limpo[0]

            horarios.append(Horario(linha.codigo, sentido, hora, dia))

    return horarios
