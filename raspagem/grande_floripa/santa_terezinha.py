from bs4 import BeautifulSoup
from common import *


URL_BASE = "https://santaterezinha.com/horarios/"
TRADUCAO = str.maketrans(
    {
        "á": "a",
        "ã": "a",
        "â": "a",
        "à": "a",
        "ó": "o",
        "õ": "o",
        "ô": "o",
        "é": "e",
        "í": "i",
        "ú": "u",
        " ": "-",
        "ç": "c",
    }
)


def raspar_linhas() -> list[Linha]:
    linhas = []

    html, status = get_html(URL_BASE)
    soup = BeautifulSoup(html, "html.parser")

    for item in soup.select(".box-body"):
        nome = extrair_texto(item.select_one("h3"))
        codigo = nome.lower().translate(TRADUCAO)
        codigo = re.sub("-+", "-", codigo)

        url = item.get("href")

        if url is None:
            url = URL_BASE + codigo + "/"

        if nome == "" or codigo == "":
            continue

        linha = Linha(codigo, nome, "", False, str(url))

        linhas.append(linha)

    return linhas


DIAS = {
    "SEGUNDA A SEXTA": "UTIL",
    "SÁBADO": "SABADO",
    "DOMINGOS E FERIADOS": "DOMINGO_FERIADO",
}


def raspar_horarios_linha(linha: Linha) -> list[Horario]:
    horarios = []
    soup, status = get_soup(linha.url)
    codigo = linha.codigo

    for tag_s in soup.select("details"):
        sentido = extrair_texto(tag_s.select_one(".e-n-accordion-item-title-text"))
        if sentido == "":
            continue

        for col in soup.select(".e-con-inner"):
            dia = extrair_texto(col.select_one("h2")).upper()

            if not dia in DIAS.keys():
                continue

            dia = DIAS[dia]

            for li in col.select(" .elementor-icon-list-text"):
                hora = extrair_texto(li)

                match = re.search("[0-9]+:[0-9]+", hora)

                if match is None:
                    continue

                hora = match.group(0)

                horario = Horario(codigo, sentido, hora, dia)

                horarios.append(horario)

    return horarios
