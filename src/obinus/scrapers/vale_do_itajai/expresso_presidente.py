from obinus.core import *
from obinus.scrapers.mobilibus import InterfaceMobilibus
from obinus.utils.http import get_soup
from obinus.utils.texto import extrair_texto


class ExpressoPresidenteGaspar(InterfaceMobilibus):
    NOME_EMPRESA = "Expresso Presidente Gaspar"
    ID_PROJETO = "699"
    REGIOES = NORTE


class ExpressoPresidenteRioMafra(InterfaceMobilibus):
    NOME_EMPRESA = "Expresso Presidente RioMafra"
    ID_PROJETO = "956"
    REGIOES = NORTE


URL_LINHAS = "https://expressopresidente.com.br/cidades/timbo/consulta-itinerario"
URL_HORARIOS = "https://expressopresidente.com.br/cidades/timbo/linha/%s"


class ExpressoPresidenteTimbo(InterfaceRaspador[Html, Html, Url]):
    NOME_EMPRESA = "EXPRESSO_PRESIDENTE_TIMBO"

    def empresa(self) -> Empresa:
        return Empresa("Expresso Presidente Timbó", regioes=VALE_DO_ITAJAI)

    def buscar_horarios(self, busca: Url) -> Html:
        return Html(get_soup(busca.url))

    def buscar_linhas(self) -> Html:
        return Html(get_soup(URL_LINHAS))

    def extrair_linhas(self, payload: Html) -> list[tuple[Linha, Url]]:
        linhas = []

        for item in payload.html.select("select#id-linha > option[value]"):
            if not (texto := extrair_texto(item)):
                continue

            codigo, nome = texto.split(" - ", maxsplit=1)
            url = URL_HORARIOS % str(item["value"])

            linhas.append((Linha(nome, codigo), Url(url)))

        return linhas

    def extrair_horarios(self, payload: Html) -> list[Servico]:
        servicos = []
        DIAS = {
            "dias-uteis": DIAS_UTEIS,
            "sabados": SABADO,
            "domingo-feriado": DOMINGO_E_FERIADOS,
        }

        for tab in payload.html.select("div.tab-content div.tab-pane "):
            if (dia := tab.get("id")) and (
                sentido := extrair_texto(tab.select_one("div.row div.row h3"))
            ):
                servico = Servico(DIAS[str(dia)], sentido)
            else:
                continue

            [
                servico.horarios.append(Horario(extrair_texto(hora)))
                for hora in tab.select("div.row div.row div.nav-box-horarios > p")
            ]

            if len(servico.horarios) != 0:
                servicos.append(servico)

        return servicos
