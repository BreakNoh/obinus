from typing import Callable, TypedDict, Optional
from obinus.core.base import Raspador
from obinus.core.modelos import Linha, Horario
from obinus.utils.http import get_json
import jmespath

from json import loads

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


TESTE = """
[{
    "routeId": 283791,
    "shortName": "100",
    "longName": "Madrugadão Centro / UFSC Norte",
    "desc": "",
    "type": 3,
    "color": "#255e81",
    "textColor": "#FFFFFF",
    "ac": false,
    "price": 6,
    "timetable": {
      "directions": [
        {
          "directionId": 1,
          "desc": "TICEN - Plataforma C - Box 6",
          "services": [
            {
              "serviceId": 308458,
              "desc": "Dias Úteis - Convencional",
              "days": [
                false,
                true,
                true,
                true,
                true,
                true,
                false
              ],
              "departures": [
                {
                  "dep": "00:45",
                  "arr": "01:40",
                  "wa": 1,
                  "seq": 1
                },
                {
                  "dep": "02:35",
                  "arr": "03:30",
                  "wa": 1,
                  "seq": 1
                },
                {
                  "dep": "04:25",
                  "arr": "05:20",
                  "wa": 1,
                  "seq": 1
                }
              ]
            },
            {
              "serviceId": 308461,
              "desc": "Sábados - Convencional",
              "days": [
                false,
                false,
                false,
                false,
                false,
                false,
                true
              ],
              "departures": [
                {
                  "dep": "00:45",
                  "arr": "01:40",
                  "wa": 1,
                  "seq": 1
                },
                {
                  "dep": "02:35",
                  "arr": "03:30",
                  "wa": 1,
                  "seq": 1
                },
                {
                  "dep": "04:25",
                  "arr": "05:20",
                  "wa": 1,
                  "seq": 1
                }
              ]
            },
            {
              "serviceId": 307430,
              "desc": "Domingos - Convencional",
              "days": [
                true,
                false,
                false,
                false,
                false,
                false,
                false
              ],
              "departures": [
                {
                  "dep": "00:45",
                  "arr": "01:40",
                  "wa": 1,
                  "seq": 1
                },
                {
                  "dep": "02:35",
                  "arr": "03:30",
                  "wa": 1,
                  "seq": 1
                },
                {
                  "dep": "04:25",
                  "arr": "05:20",
                  "wa": 1,
                  "seq": 1
                }
              ]
            }
          ]
    }
      ],
      "trips": [
        {
          "tripId": 777829,
          "tripDesc": "Trindade / Córrego Grande » TICEN",
          "shortName": "",
          "directionId": 1,
          "seq": 1
        }
      ]
    }
  }]"""


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
    resultado = QUERY_LINHAS.search(json)

    print(resultado)

    return QUERY_LINHAS.search(json)


def testar():
    json = loads(TESTE)
    # print(json)
    print(QUERY_LINHAS.search(json))


class Mobilibus(Raspador):
    def __init__(self, id_projeto: int, conversor: Callable[[str], str]):
        self.id_projeto = id_projeto
        self.converter_dia = conversor
        self.cache_json: Optional[list[Linhas]] = None

    def _carregar_dados(self):
        if self.cache_json is None:
            dados_brutos, status = get_json(
                URL_HORARIOS, {"project_id": self.id_projeto}
            )
            if status == 200:
                self.cache_json = extrair_linhas(dados_brutos)
            else:
                self.cache_json = []

    id_projeto: int = 332
    converter_dia: Callable[[str], str] = lambda s: s
    json: list[Linhas] = []

    def empresa(self) -> str:
        return "MOBILIBUS"

    def raspar_linhas(self) -> list[Linha]:
        self._carregar_dados()

        linhas = []

        if self.cache_json is None:
            return []

        for l in self.cache_json:
            print(l)
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

        if self.cache_json is None:
            return []

        for l in self.cache_json:
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
