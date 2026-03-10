from bs4 import BeautifulSoup
from common import *

URL_BASE = "https://www2.jotur.com.br/linhas/"


def raspar_linhas() -> tuple[list[Linha], list[tuple[str, str]]]:
    html, status = get_html(URL_BASE)
    soup = BeautifulSoup(html, "html.parser")

    linhas = []
    urls = []

    for item in soup.select("li>a"):
        url = item["href"]

        tag_cod = item.select_one("strong")
        tag_nome = item.select_one("span")

        if tag_cod is None or tag_nome is None:
            continue

        codigo = extrair_texto(tag_cod)
        nome = extrair_texto(tag_nome).removeprefix("- ")
        executivo = "executivo" in nome.lower()

        linha = Linha(codigo, nome, "", executivo)

        linhas.append(linha)
        urls.append((codigo, str(url)))

    return (linhas, urls)


DIAS = {
    "Dias Úteis": "UTIL",
    "Sábados": "SABADO",
    "Domingos e Feriados": "DOMINGO_FERIADO",
}


def raspar_horarios_linha(url: str, linha: str) -> list[Horario]:
    html, status = get_html(URL_BASE + url)
    soup = BeautifulSoup(html, "html.parser")

    horarios = []

    for aba in soup.select(".accordion-item"):
        tag_sentido = aba.select_one(".accordion-header > :last-child")
        sentido = extrair_texto(tag_sentido)

        if sentido == "":
            continue

        for coluna in aba.select(".column"):
            tag_dia = coluna.select_one("h4")
            dia = extrair_texto(tag_dia)

            if not dia in DIAS.keys():
                continue

            dia = DIAS[str(dia)]

            for item in coluna.select(".time-item"):
                hora = extrair_texto(item)

                if hora == "":
                    continue

                horario = Horario(linha, sentido, hora, dia)

                horarios.append(horario)

    return horarios


def raspar_horarios(urls: list[tuple[str, str]]) -> list[Horario]:
    horarios = []

    for cod, url in urls:
        print(f"Raspando horarios da linha {cod}...")
        horarios.extend(raspar_horarios_linha(url, cod))

    return horarios


print("Raspando linhas...")
linhas, urls = raspar_linhas()

salvar_csv(linhas, "out/linhas_jotur.csv")

print("Raspando horarios...")
horarios = raspar_horarios(urls)

salvar_csv(horarios, "out/horarios_jotur.csv")
