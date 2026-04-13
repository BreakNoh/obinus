from typing import TypedDict, cast
from obinus.core.raspador import InterfaceRaspador
from obinus.core.tipos import *
from obinus.utils.http import get_json, get_soup
from obinus.utils.texto import extrair_texto
from jmespath import compile


URL_BASE = "https://editor.mobilibus.com/web/timetable/1db0m"


class DadosHorario(TypedDict):
    hora: str
    acessivel: bool


class DadosSentido(TypedDict):
    sentido: str
    horas: list[DadosHorario]


class DadosServico(TypedDict):
    dia: str
    sentidos: list[DadosSentido]


QUERY_HORARIOS = compile("""
    services[].{
        dia: serviceName,
        sentidos: directions[].{
            sentido: direction,
            horas: departures[].{
                hora:time, 
                acessivel: accessible
            }
        }
    }
""")


DIAS = {
    "dia útil": DIAS_UTEIS,
    "sábado": SABADO,
    "feriado": DOMINGO_E_FERIADOS,
    "domingo": DOMINGO_E_FERIADOS,
}


class ColetivoRainha(InterfaceRaspador[Html, Json, Url]):
    def empresa(self) -> Empresa:
        return Empresa(id="CRAIN", nome="Coletivo Rainha", regioes=NORTE)

    def buscar_linhas(self) -> Html:
        html_final = BeautifulSoup()

        [html_final.append(opt) for opt in get_soup(URL_BASE).select("div[data-value]")]

        return Html(html_final)

    def extrair_linhas(self, payload: Html) -> list[tuple[Linha, Url]]:
        linhas = []

        for l in payload.html.select("div[data-value]"):
            texto = extrair_texto(l)

            if (codigo_nome := texto.split(" - ", 1)) and len(codigo_nome) == 2:
                cod, nome = codigo_nome
                id = l["data-value"]

                linhas.append((Linha(nome, cod), Url(f"{URL_BASE}/{id}")))

        return linhas

    def buscar_horarios(self, busca: Url) -> Json:
        return Json(QUERY_HORARIOS.search(get_json(busca.url)))

    def extrair_horarios(self, payload: Json) -> list[Servico]:
        servicos = []

        if not (
            json := cast(list[DadosServico], payload.json)
        ):  # define json se for válido e retorna se for inválido
            return []

        for ser in json:
            if dia := DIAS[ser["dia"].lower()]:
                for sen in ser["sentidos"]:
                    servico = Servico(dia, sen["sentido"])

                    servico.horarios.extend(
                        [
                            Horario(
                                hora["hora"], [Adaptado()] if hora["acessivel"] else []
                            )
                            for hora in sen["horas"]
                        ]
                    )

                    servicos.append(servico)

        return servicos
