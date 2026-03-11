import re
from common import *

URL_BASE = "https://www.consorciofenix.com.br"
URL_LINHAS = URL_BASE + "/horarios"


DIAS = {
    "Dias Úteis": "UTIL",
    "Sábado": "SABADO",
    "Domingos e Feriados": "DOMINGO_FERIADO",
}


def raspar_horarios_linha(linha: Linha) -> list[Horario]:
    soup, status = get_soup(linha.url)
    horarios: list[Horario] = []
    codigo = linha.codigo

    for sub in soup.select(".my-subtab-content"):
        sentido = extrair_texto(sub.select_one("h5"))

        if sentido == "":
            continue

        for horario in sub.select("div[data-semana]"):
            dia = horario.get("data-semana")
            tag_a = horario.find("a")

            if tag_a is None or dia not in DIAS:
                continue

            hora = extrair_texto(tag_a)
            dia = DIAS[str(dia)]

            horarios.append(Horario(codigo, sentido, hora, dia))

    return horarios


def raspar_linhas() -> list[Linha]:
    soup, status = get_soup(URL_LINHAS)
    linhas: list[Linha] = []

    for li in soup.select("wrap-horarios li"):
        tag_a = li.find("a")
        if tag_a is None:
            continue

        conteudo = extrair_texto(tag_a)

        [codigo, nome] = re.split(r"\s+-\s+", conteudo, maxsplit=1)

        executivo = "executivo" in nome.lower()
        codigo = codigo.strip()
        nome = nome.strip()
        url = tag_a.get("href")

        linhas.append(Linha(codigo, nome, "", executivo, str(url)))

    return linhas
