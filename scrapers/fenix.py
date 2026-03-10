import re
import sys
import requests
from bs4 import BeautifulSoup
from common import *

URL_BASE = "https://www.consorciofenix.com.br"
URL_LINHAS = URL_BASE + "/horarios"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0"
}


sessao = requests.Session()


def raspar_horario(dom: BeautifulSoup, linha: str) -> list[Horario]:
    horarios: list[Horario] = []

    for tab in dom.find_all(class_="my-tab-content"):
        for sub in tab.find_all(class_="my-subtab-content"):
            tag_sentido = sub.find("h5")
            if tag_sentido is None:
                continue

            sentido = extrair_texto(tag_sentido)

            for horario in sub.select("div[data-semana]"):
                dia = horario.get("data-semana")
                tag_a = horario.find("a")

                if tag_a is None or dia not in DIAS:
                    continue

                hora = extrair_texto(tag_a)
                dia = DIAS[str(dia)]

                horarios.append(Horario(linha, sentido, hora, dia))

    return horarios


def raspar_linhas(
    dom: BeautifulSoup, horarios: list[Horario] | None = None
) -> list[Linha]:
    linhas: list[Linha] = []

    container = dom.find(class_="wrap-horarios")

    if container is None:
        return []

    for li in container.find_all("li"):
        codigo, nome, detalhe = "", "", ""

        conteudo = ""

        tag_a = li.find("a")
        if tag_a is None:
            continue

        conteudo = extrair_texto(tag_a)

        [codigo, nome] = re.split(r"\s+-\s+", conteudo, maxsplit=1)

        executivo = "executivo" in nome.lower()
        codigo = codigo.strip()
        nome = nome.strip()

        linhas.append(Linha(codigo, nome, detalhe, executivo))

        if horarios is None:
            continue

        href = tag_a["href"]
        html_hora = sessao.get(URL_BASE + str(href), headers=headers).text

        print("Ranspando horarios da linha:", codigo, nome, "...")

        horarios.extend(raspar_horario(BeautifulSoup(html_hora, "html.parser"), codigo))

    return linhas


DIAS = {
    "Dias Úteis": "UTIL",
    "Sábado": "SABADO",
    "Domingos e Feriados": "DOMINGO_FERIADO",
}


html_linhas = sessao.get(URL_LINHAS, headers=headers).text

horarios: list[Horario] = []
linhas: list[Linha] = []

print("Raspando linhas...")

linhas = raspar_linhas(
    BeautifulSoup(html_linhas, "html.parser"),
    horarios if not "--linhas" in sys.argv else None,
)
salvar_csv(linhas, "out/linhas_fenix.csv")
salvar_csv(horarios, "out/horarios_fenix.csv")
