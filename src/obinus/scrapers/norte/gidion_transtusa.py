from typing import TypedDict
from obinus.core.base import Raspador
from obinus.core.modelos import Linha, Horario
from jmespath import compile

from obinus.utils.http import get_json


URL_BASE = "https://onibus.info"
URL_HORARIOS = URL_BASE + "/api/timetableschedule/"
URL_LINHAS = URL_BASE + "/api/routes/group"


class DadosLinha(TypedDict):
    codigo: str
    nome: str


class DadosHora(TypedDict):
    dia: str
    horas: list[str]


class DadosHorarios(TypedDict):
    sentido: str
    horarios: list[DadosHora]


QUERY_LINHAS = compile("""
    [*].routes[].{
        codigo: route_id, 
        nome: route_long_name
    }
""")
QUERY_HORARIOS = compile("""
    [*].{
        sentido: direction,
        horarios: stop_data[].service_data[].{
            dia: service_id,
            horas: time_data[][].departure_time
        }
    }
""")

headers = {"Referer": URL_BASE + "/linhas"}


class GidionTranstusa(Raspador):
    def empresa(self) -> str:
        return "GIDION_TRANSTUSA"

    def raspar_linhas(self) -> list[Linha]:
        json, status = get_json(URL_LINHAS, headers=headers)

        linhas: list[Linha] = []

        query: list[DadosLinha] = QUERY_LINHAS.search(json)

        if query is []:
            return []

        for l in query:
            linha = Linha(
                empresa=self.empresa(),
                nome=l["nome"],
                codigo=l["codigo"],
                detalhe="",
                executivo=False,
            )

            linhas.append(linha)

        return linhas

    def raspar_horarios_linha(self, linha: Linha) -> list[Horario]:
        json, status = get_json(URL_HORARIOS + linha.codigo, headers=headers)

        horarios: list[Horario] = []

        query: list[DadosHorarios] = QUERY_HORARIOS.search(json)

        if query is []:
            return []

        for ser in query:
            sentido = ser["sentido"]

            for d in ser["horarios"]:
                dia = d["dia"]

                horarios.extend(
                    [
                        Horario(
                            empresa=self.empresa(),
                            linha=linha.codigo,
                            sentido=sentido,
                            hora=hora,
                            dia=dia,
                        )
                        for hora in d["horas"]
                    ]
                )

        self.esperar()
        return horarios
