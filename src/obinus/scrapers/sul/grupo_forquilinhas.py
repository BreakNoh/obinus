import re
from obinus.core import *
from obinus.utils.http import extrair_texto, get_soup

URL = "https://www.grupoforquilhinha.com.br/horarios"


class GrupoForquilhinhas(InterfaceRaspador[Html, Html, Html]):
    def empresa(self) -> Empresa:
        return Empresa(id="grupo-forquilinha", nome="Grupo Forquilinha", regioes=GRANDE_FLORIPA | SUL)

    def buscar_linhas(self) -> Html:
        return Html(get_soup(URL))

    def buscar_horarios(self, busca: Html) -> Html:
        return busca

    def extrair_linhas(self, payload: Html) -> list[tuple[Linha, Html]]:
        SELETOR_LINHAS = "div.c-tab-linha"
        SELETOR_COD_E_NOME = "a > h3"
        SELETOR_DETALHE = "a > p"
        linhas = []

        for linha in payload.html.select(SELETOR_LINHAS):
            if nome_inteiro := extrair_texto(linha.select_one(SELETOR_COD_E_NOME)):
                codigo, nome = nome_inteiro.split(" - ", maxsplit=1)
            else:
                continue

            detalhe = extrair_texto(linha.select_one(SELETOR_DETALHE))

            if not (info_linha := linha.select_one("a")):
                continue

            id_tabela = str(info_linha.get("data-tipo"))

            if not (tabela := payload.html.select_one(f"[id='{id_tabela}']")):
                continue

            linhas.append((Linha(nome, codigo, detalhe), Html(tabela)))

        return linhas

    def extrair_horarios(self, payload: Html) -> list[Servico]:
        PADRAO_HORARIOS = re.compile(r"(?P<hora>\d{2}:\d{2})(?P<obs>[A-Z])?")
        PADRAO_ITINERARIO = re.compile(r"(?:\d+)(.)")
        SELETOR_SENTIDO = 'div.horariosPartida > div[class^="column"]'
        SELETOR_DIA_HORARIOS = (
            "div.daysHours :is(h5, li > p)"  # fluxo dia, horarios, dia, horarios, ...
        )

        DIAS = {
            "segunda-feira a sexta-feira": DIAS_UTEIS,
            "sábados": SABADO,
            "domingos e feriados": DOMINGO_E_FERIADOS,
        }

        servicos = []

        for coluna in payload.html.select(SELETOR_SENTIDO):
            if not (sentido := extrair_texto(coluna.select_one("h4"))):
                continue

            servico = None

            for item in coluna.select(SELETOR_DIA_HORARIOS):
                match item.name:
                    case "h5" if dia_raw := extrair_texto(item):
                        if servico and len(servico.horarios) > 0:
                            servicos.append(servico)

                        servico = Servico(DIAS[dia_raw.lower()], sentido)
                    case "p" if (
                        servico
                        and (texto := extrair_texto(item))
                        and (match := PADRAO_HORARIOS.search(texto))
                    ):
                        horario = Horario(match.group("hora"))

                        if itin := match.group("obs"):
                            horario.obs.append(ItinerarioDiferenciado(itin))

                        servico.horarios.append(horario)

            if servico and len(servico.horarios) > 0:
                servicos.append(servico)

        return servicos
