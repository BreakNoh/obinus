from typing import TypedDict, cast
from obinus.core.raspador import InterfaceRaspador
from obinus.core.tipos import *
from jmespath import compile
from obinus.utils.http import get_json


URL_BASE = "https://onibus.info"
URL_HORARIOS = URL_BASE + "/api/timetable/%s"
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
    [].routes[].{
        codigo: route_id, 
        nome: route_long_name
    }
""")

QUERY_HORARIOS = compile("""
    [].{
        sentido: direction,
        horarios: stop_data[].service_data[].{
            dia: service_id,
            horas: time_data[][].departure_time
        }
    }
""")

headers = {"Referer": URL_BASE + "/linhas"}

DIAS = {"DU": DIAS_UTEIS, "SAB": SABADO, "DOM": DOMINGO_E_FERIADOS}


class GidionTranstusa(InterfaceRaspador[Json, Json, Raw]):
    def empresa(self) -> Empresa:
        return Empresa(
            id="gidion-transtusa",
            nome="Gidion/Transtusa",
            regioes=NORTE,
            fonte="https://onibus.info",
        )

    def buscar_linhas(self) -> Json:
        return Json(QUERY_LINHAS.search(get_json(URL_LINHAS, headers=headers)))

    def buscar_horarios(self, busca: Raw) -> Json:
        return Json(
            QUERY_HORARIOS.search(get_json(URL_HORARIOS % busca.valor, headers=headers))
        )

    def extrair_linhas(self, payload: Json) -> list[tuple[Linha, Raw]]:
        linhas = []

        if json := cast(list[DadosLinha], payload.json):
            [
                linhas.append((Linha(l["nome"], l["codigo"]), Raw(l["codigo"])))
                for l in json
            ]

        return linhas

    def extrair_horarios(self, payload: Json) -> list[Servico]:
        servicos = []

        if json := cast(list[DadosHorarios], payload.json):
            for ser in json:
                sentido = ser["sentido"]

                for d in ser["horarios"]:
                    dia = d["dia"]
                    servico = Servico(DIAS[dia.upper()], sentido)

                    servico.horarios.extend(
                        [
                            Horario(
                                hora=hora,
                            )
                            for hora in d["horas"]
                        ]
                    )

                    servicos.append(servico)

        return servicos
