from bs4 import BeautifulSoup, Tag
from bs4.element import PageElement
from obinus.core.base import Raspador
from obinus.core.modelos import Linha, Horario
from obinus.utils.http import get_soup, extrair_texto

URL = "https://icarense.com.br/linhas-e-horarios/"


class ExpressoIcarense(Raspador):
    NOME_EMPRESA = "EXPRESSO_ICARENSE"
    _cache: BeautifulSoup | None = None

    def _carregar_soup(self) -> BeautifulSoup:
        if self._cache:
            return self._cache
        else:
            soup, status = get_soup(URL)

            self._cache = soup
            return self._cache

    def raspar_linhas(self) -> list[Linha]:
        soup = self._carregar_soup()

        dia: str | None = None
        linhas = []

        for tab_dia in soup.select(".e-n-tabs-content > div"):
            if tab_dia.has_attr("role"):  # header
                dia = extrair_texto(tab_dia.select_one("a"))
                continue

            blocos_linhas = tab_dia.find(class_="jet-listing-grid__items")

            if not blocos_linhas or not dia:
                continue

            for bloco in blocos_linhas.find_all(
                class_="jet-listing-grid__item", recursive=False
            ):  # conteudo (linhas)
                nome = extrair_texto(bloco.select_one(".fa-bus-alt + div"))

                metadados = (dia, bloco.select(".jet-listing-grid__item"))

                if not nome:
                    continue

                linhas.append(
                    Linha(
                        empresa=self.NOME_EMPRESA,
                        codigo="",
                        nome=nome,
                        metadados=metadados,
                    )
                )

        return linhas

    def raspar_horarios_linha(self, linha: Linha) -> list[Horario]:
        if not linha.metadados or not isinstance(linha.metadados, tuple):
            return []

        horarios = []
        dia, blocos = linha.metadados

        for horario in blocos:  # itens tabela horario
            infos = [
                extrair_texto(t)
                for t in horario.select(".jet-listing-dynamic-field__content")
            ]

            if len(infos) != 2:
                continue

            hora, sentido = infos

            if not hora or not sentido:
                continue

            horarios.append(
                Horario(
                    empresa=self.NOME_EMPRESA,
                    linha=linha.nome,
                    sentido=sentido,
                    hora=hora,
                    dia=dia,
                )
            )
            # print(infos)
        return horarios
