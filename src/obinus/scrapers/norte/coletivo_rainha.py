from typing import TypedDict
from obinus.core.base import Raspador
from obinus.core.modelos import Linha, Horario
from obinus.utils.http import get_json, get_soup
from obinus.utils.texto import extrair_texto
from jmespath import compile


URL_BASE = "https://editor.mobilibus.com/web/timetable/1db0m"


class Sentido(TypedDict):
    sentido: str
    horas: list[str]


class Servico(TypedDict):
    dia: str
    sentidos: list[Sentido]


QUERY_HORARIOS = compile("""
    services[].{
        dia: serviceName,
        sentidos: directions[].{
            sentido: direction,
            horas: departures[].time
        }
    }
""")


class ColetivoRainha(Raspador):
    def empresa(self) -> str:
        return "COLETIVO_RAINHA"

    def raspar_linhas(self) -> list[Linha]:
        soup, status = get_soup(URL_BASE)
        linhas = []

        for l in soup.select("#routes option[value]"):
            texto = extrair_texto(l)

            codigo, nome = texto.split(" - ", 1)
            _id = l["value"]

            linha = Linha(
                empresa=self.empresa(),
                nome=nome,
                codigo=codigo,
                detalhe="",
                url=URL_BASE + "/" + str(_id),
            )

            linhas.append(linha)

        return linhas

    def raspar_horarios_linha(self, linha: Linha) -> list[Horario]:
        json, status = get_json(linha.url)

        horarios = []

        query: list[Servico] = QUERY_HORARIOS.search(json)

        if query is [] or query is None:
            return []

        for ser in query:
            dia = ser["dia"]

            for sen in ser["sentidos"]:
                sentido = sen["sentido"]

                horarios.extend(
                    [
                        Horario(
                            empresa=self.empresa(),
                            linha=linha.codigo,
                            sentido=sentido,
                            hora=hora,
                            dia=dia,
                        )
                        for hora in sen["horas"]
                    ]
                )

        self.esperar()
        return horarios
