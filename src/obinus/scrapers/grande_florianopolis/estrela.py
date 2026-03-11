import re

from obinus.core.base import Raspador
from obinus.core.modelos import Linha, Horario
from obinus.utils.http import get_soup
from obinus.utils.texto import extrair_texto

EMPRESA: str = "ESTRELA"

URL_BASE = "https://insulartc.com.br"
URL_LINHAS = URL_BASE + "/est/wp/"
DIAS = ["UTIL", "UTIL", "UTIL", "SABADO", "SABADO", "DOMINGO_FERIADO"]


class Estrela(Raspador):
    def empresa(self) -> str:
        return EMPRESA

    def raspar_linhas(self) -> list[Linha]:
        soup, status = get_soup(URL_LINHAS)
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

            linhas.append(Linha(EMPRESA, codigo, nome, "", executivo, url))

        return linhas

    def raspar_horarios_linha(self, linha: Linha) -> list[Horario]:
        soup, status = get_soup(linha.url)
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

                horarios.append(Horario(EMPRESA, linha.codigo, sentido, hora, dia))

        return horarios
