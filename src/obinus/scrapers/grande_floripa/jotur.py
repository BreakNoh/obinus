from obinus.core.base import Raspador
from obinus.core.modelos import Linha, Horario
from obinus.utils.http import get_soup
from obinus.utils.texto import extrair_texto

EMPRESA: str = "JOTUR"

URL_BASE = "https://www2.jotur.com.br/linhas/"
DIAS = {
    "Dias Úteis": "UTIL",
    "Sábados": "SABADO",
    "Domingos e Feriados": "DOMINGO_FERIADO",
}


class Jotur(Raspador):
    def empresa(self) -> str:
        return EMPRESA

    def raspar_linhas(self) -> list[Linha]:
        soup, status = get_soup(URL_BASE)

        linhas = []

        for item in soup.select("li>a"):
            url = item["href"]

            tag_cod = item.select_one("strong")
            tag_nome = item.select_one("span")

            if tag_cod is None or tag_nome is None:
                continue

            codigo = extrair_texto(tag_cod)
            nome = extrair_texto(tag_nome).removeprefix("- ")
            executivo = "executivo" in nome.lower()

            linha = Linha(EMPRESA, codigo, nome, "", executivo, URL_BASE + str(url))

            linhas.append(linha)

        return linhas

    def raspar_horarios_linha(self, linha: Linha) -> list[Horario]:
        soup, status = get_soup(linha.url)

        horarios = []
        codigo = linha.codigo

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

                    horario = Horario(EMPRESA, codigo, sentido, hora, dia)

                    horarios.append(horario)

        return horarios
