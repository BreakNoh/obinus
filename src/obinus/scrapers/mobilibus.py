from typing import TypedDict
from obinus.core.base import Raspador
from obinus.core.modelos import Linha, Horario
from obinus.utils.http import get_json
import jmespath

URL_LINHAS = "https://mobilibus.com/api/routes"
URL_HORARIOS = "https://mobilibus.com/api/timetable"


class DadosDia(TypedDict):
    dia: str
    horas: list[str]


class DadosHorarios(TypedDict):
    sentido: str
    dias: list[DadosDia]


class DadosLinha(TypedDict):
    id_rota: int
    nome: str
    codigo: str
    detalhe: str


QUERY_HORARIOS = """
    [?shortName==`"%s"`].timetable.directions[].{
        sentido: desc,
        dias: services[].{
            dia: desc,
            horas: departures[].dep
        }
    }
"""

QUERY_LINHAS = jmespath.compile("""
    [].{
        id_rota: routeId,
        nome: longName,
        codigo: shortName,
        detalhe: desc
    }
""")


class Mobilibus(Raspador):
    ID_PROJETO: str
    VERSAO_LINHAS: str = "1"
    VERSAO_HORARIOS: str = "1"

    def raspar_linhas(self) -> list[Linha]:
        json, status = get_json(
            URL_LINHAS, params={"project_id": self.ID_PROJETO, "v": self.VERSAO_LINHAS}
        )

        linhas = []

        query: list[DadosLinha] = QUERY_LINHAS.search(json)

        if query is None or query == []:
            return []

        for l in query:
            codigo = l["codigo"]
            nome = l["nome"]
            detalhe = l["detalhe"]
            executivo = "executivo" in nome.lower()

            linha = Linha(
                empresa=self.NOME_EMPRESA,
                codigo=codigo,
                nome=nome,
                detalhe=detalhe,
                executivo=executivo,
                url=URL_HORARIOS
                + f"?project_id={self.ID_PROJETO}"
                + f"&route_id={l['id_rota']}"
                + f"&v={self.VERSAO_HORARIOS}",
            )

            linhas.append(linha)

        return linhas

    def raspar_horarios_linha(self, linha: Linha) -> list[Horario]:
        json, status = get_json(linha.url)

        horarios = []

        query: list[DadosHorarios] = jmespath.search(
            QUERY_HORARIOS % linha.codigo, json
        )

        if query is None or query == []:
            return []

        for ser in query:
            sentido = ser["sentido"]

            for d in ser["dias"]:
                dia = self.normalizar_dia(d["dia"])

                horarios.extend(
                    [
                        Horario(
                            empresa=self.NOME_EMPRESA,
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
