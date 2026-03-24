from bs4 import BeautifulSoup
from obinus.core.base import Raspador
from obinus.core.modelos import Linha, Horario
from obinus.utils.http import extrair_texto, get_soup

URL = "https://www.grupoforquilhinha.com.br/horarios"

SELETOR_LINHAS = ".c-tab-linha"
SELETOR_COD_E_NOME = "a > h3"
SELETOR_DETALHE = "a > p"

SELETOR_SENTIDO = '[id="%s"] .horariosPartida > div[class^="column"]'
SELETOR_NOME_SENTIDO = "h4"
SELETOR_DIA_HORARIOS = (
    ".daysHours :is(h5, li > p)"  # fluxo dia, horarios, dia, horarios, ...
)


class GrupoForquilhinha(Raspador):
    NOME_EMPRESA = "GRUPO_FORQUILINHA"
    _cache: BeautifulSoup | None = None

    def raspar_horarios_linha(self, linha: Linha) -> list[Horario]:
        if not linha.metadados or not self._cache:
            return []

        id = linha.metadados
        horarios = []

        for coluna in self._cache.select(SELETOR_SENTIDO % id):
            sentido = extrair_texto(coluna.select_one(SELETOR_NOME_SENTIDO))
            dia: list[str] | str = []

            if not sentido:
                continue

            for item in coluna.select(SELETOR_DIA_HORARIOS):
                # print(item.name, dia)
                match item.name:
                    case "h5":
                        if dia_raw := extrair_texto(item):
                            dia = self.normalizar_dia(dia_raw)
                        else:
                            continue
                    case "p":
                        if hora_raw := extrair_texto(item):
                            horarios.append(
                                Horario(
                                    empresa=self.NOME_EMPRESA,
                                    hora=hora_raw,
                                    linha=linha.codigo,
                                    dia=dia,
                                    sentido=sentido,
                                )
                            )
                        else:
                            continue

        return horarios

    def raspar_linhas(self) -> list[Linha]:
        soup, _ = get_soup(URL)
        linhas = []
        self._cache = soup

        for linha in soup.select(SELETOR_LINHAS):
            codigo: str
            nome: str
            meta: str | None = None

            if nome_inteiro := extrair_texto(linha.select_one(SELETOR_COD_E_NOME)):
                codigo, nome = nome_inteiro.split(" - ", maxsplit=1)
            else:
                continue

            detalhe: str | None = extrair_texto(linha.select_one(SELETOR_DETALHE))

            if info_linha := linha.select_one("a"):
                meta = str(info_linha.get("data-tipo"))

            if not detalhe:
                continue

            linhas.append(
                Linha(
                    empresa=self.NOME_EMPRESA,
                    codigo=codigo,
                    nome=nome,
                    detalhe=detalhe,
                    metadados=meta,
                )
            )

        return linhas
