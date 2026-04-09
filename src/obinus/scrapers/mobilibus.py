from typing import TypedDict, cast
from obinus.core.raspador import InterfaceRaspador
from obinus.core.tipos import *
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

DIAS = {"dias úteis": DIAS_UTEIS, "sábados": SABADO, "domingos": DOMINGO_E_FERIADOS}


class InterfaceMobilibus(InterfaceRaspador[Json, Json, Url]):
    NOME_EMPRESA: str
    REGIOES: Regioes
    ID_PROJETO: str
    VERSAO_LINHAS: str = "1"
    VERSAO_HORARIOS: str = "1"

    def empresa(self) -> Empresa:
        return Empresa(nome=self.NOME_EMPRESA, regioes=self.REGIOES)

    def extrair_horarios(self, payload: Json) -> list[Servico]:
        servicos = []

        if json := cast(list[DadosHorarios], payload.json):
            for ser in json:
                sentido = ser["sentido"]

                for dia in ser["dias"]:
                    dia_norm = dia["dia"].lower().strip()
                    servico = Servico(DIAS[dia_norm], sentido)

                    [servico.horarios.append(Horario(h)) for h in dia["horas"]]

                    servicos.append(servico)

        return servicos

    def extrair_linhas(self, payload: Json) -> list[tuple[Linha, Url]]:
        linhas = []

        if json := cast(list[DadosLinha], payload.json):
            for lin in json:
                nome = (
                    lin["nome"]
                    if lin["nome"] == "" or not lin["nome"]
                    else lin["codigo"]
                )
                codigo = lin["codigo"] if nome != lin["nome"] else None
                url = f"{URL_HORARIOS}?project_id={self.ID_PROJETO}&route_id={lin['id_rota']}&v={self.VERSAO_HORARIOS}"
                linhas.append((Linha(nome=nome, codigo=codigo), Url(url)))

        return linhas

    def buscar_horarios(self, busca: Url) -> Json:
        json = get_json(busca.url)

        return Json(QUERY_LINHAS.search(json))

    def buscar_linhas(self) -> Json:
        json = get_json(
            URL_LINHAS, params={"project_id": self.ID_PROJETO, "v": self.VERSAO_LINHAS}
        )

        return Json(QUERY_LINHAS.search(json))
