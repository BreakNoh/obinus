import re
from obinus.core.base import Raspador
from obinus.core.modelos import Linha, Horario
from obinus.utils.http import get_soup
from obinus.utils.texto import extrair_texto

from obinus.core.raspador import InterfaceRaspador
from obinus.core.tipos import *


EMPRESA: str = "FENIX"

URL_LINHAS = "https://www.consorciofenix.com.br/horarios"
URL_BASE = "https://www.consorciofenix.com.br"

DIAS = {}


def parsear_dias(d: str) -> Dias:
    match d.lower():
        case "dias úteis":
            return DIAS_UTEIS
        case "sábado":
            return SABADO
        case "domingos e feriados":
            return DOMINGO_E_FERIADOS
        case _:
            return 0


class RaspadorFenix(InterfaceRaspador[Html, Html, Url]):
    def extrair_linhas(self, payload: Html) -> list[tuple[Linha_, Url]]:
        linhas = []

        for item in payload.html.select(".wrap-horarios li a"):
            conteudo = extrair_texto(item)

            [codigo, nome] = re.split(r"\s+-\s+", conteudo, maxsplit=1)

            executivo = "executivo" in nome.lower()
            codigo = codigo.strip()
            nome = nome.strip()
            url = URL_BASE + str(item.get("href"))

            linha = Linha_(nome=nome, codigo=codigo)
            if executivo:
                linha.tipo = TipoLinha.EXECUTIVO

            linhas.append((linha, Url(url)))

        return linhas

    def extrair_horarios(self, payload: Html) -> list[Servico]:
        servicos: list[Servico] = []
        servico_atual: Servico | None = None

        for sub in payload.html.select(".my-subtab-content"):
            sentido = extrair_texto(sub.select_one("h5"))
            servico_atual = None

            for horario in sub.select("div[data-semana][data-horario]"):
                if d := horario.get("data-semana"):
                    servico_atual = Servico(dias=parsear_dias(str(d)), sentido=sentido)

                if (hora := extrair_texto(horario.find("a"))) and servico_atual:
                    servico_atual.horarios.append(Horario_(hora))

            if servico_atual:
                servicos.append(servico_atual)

        return servicos

    def buscar_linhas(self) -> Html:
        soup, _ = get_soup(URL_LINHAS)
        return Html(soup)

    def buscar_horarios(self, busca: Url) -> Html:
        soup, _ = get_soup(busca.url)
        return Html(soup)


class Fenix(Raspador):
    def empresa(self) -> str:
        return EMPRESA

    def raspar_horarios_linha(self, linha: Linha) -> list[Horario]:
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

                horarios.append(Horario(EMPRESA, codigo, sentido, hora, dia))

        return horarios

    def raspar_linhas(self) -> list[Linha]:
        soup, status = get_soup(URL_BASE + "/horarios")
        linhas: list[Linha] = []

        for li in soup.select(".wrap-horarios li"):
            tag_a = li.find("a")

            if tag_a is None:
                continue

            conteudo = extrair_texto(tag_a)

            [codigo, nome] = re.split(r"\s+-\s+", conteudo, maxsplit=1)

            executivo = "executivo" in nome.lower()
            codigo = codigo.strip()
            nome = nome.strip()
            url = URL_BASE + str(tag_a.get("href"))

            linhas.append(Linha(EMPRESA, codigo, nome, "", executivo, url))

        return linhas
