from typing import Callable, TypedDict, Optional
from obinus.core.base import Raspador
from obinus.core.modelos import Linha, Horario
from obinus.utils.http import get_json
import jmespath

URL_LINHAS = "https://mobilibus.com/api/routes"
URL_HORARIOS = "https://mobilibus.com/api/timetable"


class Dias(TypedDict):
    dia: str
    horas: list[str]


class Horarios(TypedDict):
    sentido: str
    dias: list[Dias]


class Linhas(TypedDict):
    nome: str
    codigo: str
    detalhe: str
    horarios: list[Horarios]


QUERY_LINHAS = jmespath.compile("""
    [*].{
        nome: longName,
        codigo: shortName,
        detalhe: desc,

        horarios: timetable.directions[*].{
            sentido: desc,
            dias: services[*].{
                dia: desc,
                horas: departures[*].dep
            }
        }
    }
    """)


def extrair_linhas(json: dict) -> list[Linhas]:
    return QUERY_LINHAS.search(json)


class Mobilibus(Raspador):
    def __init__(self, id_projeto: int, conversor: Callable[[str], str]):
        self.id_projeto = id_projeto
        self.converter_dia = conversor
        self.cache_json: Optional[list[Linhas]] = None

    def _carregar_dados(self):
        if self.cache_json is None:
            dados_brutos, status = get_json(
                URL_HORARIOS, {"id_project": self.id_projeto}
            )
            if status == 200:
                self.cache_json = extrair_linhas(dados_brutos)
            else:
                self.cache_json = []

    id_projeto: int
    converter_dia: Callable[[str], str]
    json: list[Linhas] = []

    def raspar_linhas(self) -> list[Linha]:
        self._carregar_dados()

        linhas = []

        for l in self.json:
            codigo = l["codigo"]
            nome = l["nome"]
            detalhe = l["detalhe"]
            executivo = "executivo" in nome.lower()

            linha = Linha(
                empresa=self.empresa(),
                codigo=codigo,
                nome=nome,
                detalhe=detalhe,
                executivo=executivo,
            )

            linhas.append(linha)

        return linhas

    def raspar_horarios_linha(self, linha: Linha) -> list[Horario]:
        self._carregar_dados()

        horarios = []

        for l in self.json:
            if l["codigo"] != linha.codigo:
                continue

            for h in l["horarios"]:
                for d in h["dias"]:
                    for hr in d["horas"]:
                        horario = Horario(
                            empresa=self.empresa(),
                            linha=l["codigo"],
                            sentido=h["sentido"],
                            hora=hr,
                            dia=self.converter_dia(d["dia"]),
                        )
                        horarios.append(horario)

        return horarios
