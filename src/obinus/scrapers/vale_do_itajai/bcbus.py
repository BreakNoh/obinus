import re
from typing import Optional

from bs4 import BeautifulSoup, Tag
from obinus.core.base import Raspador
from obinus.core.modelos import Linha, Horario
from obinus.utils.http import get_soup
from obinus.utils.texto import extrair_texto

URL: str = "https://bcbus.com.br/"


class BCBus(Raspador):
    NOME_EMPRESA = "BCBUS"
    _cache: Optional[tuple[BeautifulSoup, int]]

    def __init__(self) -> None:
        self._cache = None

    def _carregar_soup(self) -> tuple[BeautifulSoup, int]:
        if self._cache:
            return self._cache
        else:
            self._cache = get_soup(URL)
            return self._cache

    def raspar_linhas(self) -> list[Linha]:
        soup, status = self._carregar_soup()

        linhas = []

        for info in soup.select(".et_pb_equal_columns"):
            nome = extrair_texto(info.select_one(":first-child h3 span"))
            detalhe = extrair_texto(info.select_one(":first-child h2"))

            linha = Linha(
                empresa=self.NOME_EMPRESA,
                codigo="",
                detalhe=detalhe,
                nome=nome,
                metadados=(info, detalhe),
            )

            linhas.append(linha)

        return linhas

    def normalizar_dia(self, d: str) -> str | list[str]:
        match d:
            case "SEGUNDA A SEXTA":
                return "UTIL"
            case "SÁBADOS":
                return "SABADO"
            case "DOMINGOS E FERIADOS":
                return "DOMINGO_FERIADO"
            case "DIARIAMENTE" | "TODOS OS DIAS":
                return ["UTIL", "SABADO", "DOMINGO_FERIADO"]
        return ""

    def raspar_horarios_linha(self, linha: Linha) -> list[Horario]:
        tag, sentido = linha.metadados
        horarios = []

        if not isinstance(tag, Tag):
            return []

        for coluna in tag.select("div + div"):
            dia = extrair_texto(coluna.select_one("h3:first-child"))

            sentido = (
                extrair_texto(coluna.select_one("h3 + h3"))
                if sentido == ""
                else sentido
            )

            for item in coluna.select("li"):
                match = re.match(r"(\d{2}h\d{2})", extrair_texto(item))

                if not match:
                    continue

                hora = match.group(0).lower().replace("h", ":")

                horario = Horario(
                    empresa=self.NOME_EMPRESA,
                    linha=linha.nome,
                    sentido=sentido,
                    hora=hora,
                    dia=self.normalizar_dia(dia),
                )

                horarios.append(horario)

        return horarios
