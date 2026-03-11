from obinus.core.base import Raspador
from obinus.core.modelos import Linha, Horario
from obinus.utils.http import get_soup
from obinus.utils.texto import extrair_texto
import re

EMPRESA: str = "SANTA_TEREZINHA"


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
DIAS = {
    "SEGUNDA A SEXTA": "UTIL",
    "SÁBADO": "SABADO",
    "DOMINGOS E FERIADOS": "DOMINGO_FERIADO",
}


class SantaTerezinha(Raspador):
    def empresa(self) -> str:
        return EMPRESA

    def raspar_linhas(self) -> list[Linha]:
        linhas = []

        soup, status = get_soup(URL_BASE)

        for item in soup.select(".box-body"):
            nome = extrair_texto(item.select_one("h3"))
            codigo = nome.lower().translate(TRADUCAO)
            codigo = re.sub("-+", "-", codigo)

            url = item.get("href")

            if url is None:
                url = URL_BASE + codigo + "/"

            if nome == "" or codigo == "":
                continue

            linha = Linha(EMPRESA, codigo, nome, "", False, str(url))

            linhas.append(linha)

        return linhas

    def raspar_horarios_linha(self, linha: Linha) -> list[Horario]:
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

                    horario = Horario(EMPRESA, codigo, sentido, hora, dia)

                    horarios.append(horario)

        return horarios
