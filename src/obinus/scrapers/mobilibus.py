from typing import TypedDict, cast
from obinus.core.raspador import InterfaceRaspador
from obinus.core.tipos import *
from obinus.utils.http import get_json
import jmespath

from obinus.utils.texto import normalizar_dia

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


# pega o primeiro item da lista ou o objeto raiz, depende do que a api manda
# a api pode mandar um ou outro por causa da versão
QUERY_HORARIOS = jmespath.compile("""
    ([0] || @).timetable.directions[].{ 
        sentido: desc,
        dias: services[].{
            dia: desc,
            horas: departures[].dep
        }
    }
""")

QUERY_LINHAS = jmespath.compile("""
    [].{
        id_rota: routeId,
        nome: longName,
        codigo: shortName,
        detalhe: desc
    }
""")


class InterfaceMobilibus(InterfaceRaspador[Json, Json, Url]):
    ID_EMPRESA: str
    NOME_EMPRESA: str
    REGIOES: Regioes
    ID_PROJETO: str
    FONTE: str
    VERSAO_LINHAS: str = "1"
    VERSAO_HORARIOS: str = "1"

    def empresa(self) -> Empresa:
        return Empresa(
            id=self.ID_EMPRESA,
            nome=self.NOME_EMPRESA,
            regioes=self.REGIOES,
            fonte=self.FONTE,
        )

    def extrair_horarios(self, payload: Json) -> list[Servico]:
        servicos = []

        if json := cast(list[DadosHorarios], payload.json):
            for ser in json:
                sentido = ser["sentido"]

                for dia in ser["dias"]:
                    servico = Servico(normalizar_dia(dia["dia"]), sentido)

                    [servico.horarios.append(Horario(h)) for h in dia["horas"]]

                    servicos.append(servico)

        return servicos

    def extrair_linhas(self, payload: Json) -> list[tuple[Linha, Url]]:
        linhas = []

        if json := cast(list[DadosLinha], payload.json):
            for lin in json:
                if lin["nome"] and lin["nome"] != "":
                    nome = lin["nome"]
                    codigo = lin["codigo"]
                else:
                    nome = lin["codigo"]
                    codigo = None

                url = f"{URL_HORARIOS}?project_id={self.ID_PROJETO}&route_id={lin['id_rota']}"
                linhas.append((Linha(nome=nome, codigo=codigo), Url(url)))

        return linhas

    def buscar_horarios(self, busca: Url) -> Json:
        json = ""

        try:
            for i in range(2):
                json = get_json(busca.url + (f"&v={i}" if i > 0 else ""))
                self._esperar()
        except Exception as e:
            if json == "":
                raise e

        return Json(QUERY_HORARIOS.search(json))

    def buscar_linhas(self) -> Json:
        json = get_json(
            URL_LINHAS, params={"project_id": self.ID_PROJETO, "v": self.VERSAO_LINHAS}
        )

        return Json(QUERY_LINHAS.search(json))
