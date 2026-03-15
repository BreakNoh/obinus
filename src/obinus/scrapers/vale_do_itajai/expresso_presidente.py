from obinus.core.base import Raspador
from obinus.core.modelos import Linha, Horario
from obinus.scrapers.mobilibus import Mobilibus
from obinus.utils.http import get_soup
from obinus.utils.texto import extrair_texto


class ExpressoPresidenteGaspar(Mobilibus):
    NOME_EMPRESA = "EXPRESSO_PRESIDENTE_GASPAR"
    ID_PROJETO = "699"


class ExpressoPresidenteRioMafra(Mobilibus):
    NOME_EMPRESA = "EXPRESSO_PRESIDENTE_RIOMAFRA"
    ID_PROJETO = "956"


URL_LINHAS = "https://expressopresidente.com.br/cidades/timbo/consulta-itinerario"
URL_HORAIOS = "https://expressopresidente.com.br/cidades/timbo/linha/%s"


class ExpressoPresidenteTimbo(Raspador):
    NOME_EMPRESA = "EXPRESSO_PRESIDENTE_TIMBO"

    def raspar_linhas(self) -> list[Linha]:
        soup, status = get_soup(URL_LINHAS)
        linhas = []

        for opt in soup.select("#id-linha option"):
            texto = extrair_texto(opt)
            codigo, nome = texto.split(" - ", maxsplit=1)

            url = opt.get("value")

            if not codigo or not nome or not url:
                continue

            linha = Linha(
                empresa=self.NOME_EMPRESA,
                codigo=codigo,
                nome=nome,
                url=URL_HORAIOS % url,
                detalhe="",
            )

            linhas.append(linha)

        return linhas

    def normalizar_dia(self, d: str) -> str | list[str]:
        match d:
            case "dias-uteis":
                return "UTIL"
            case "sabados":
                return "SABADO"
            case "domingo-feriado":
                return "DOMINGO_FERIADO"

        return ""

    def raspar_horarios_linha(self, linha: Linha) -> list[Horario]:
        soup, status = get_soup(linha.url)
        horarios = []

        for tab in soup.select(".tab-content > div"):
            dia = tab.get("id")
            sentido = extrair_texto(tab.select_one("h3"))

            horas = [extrair_texto(hora) for hora in tab.select(".nav-box-horarios p")]

            if not dia or not sentido or not horas:
                continue

            horarios.extend(
                [
                    Horario(
                        empresa=self.NOME_EMPRESA,
                        linha=linha.codigo,
                        sentido=sentido,
                        hora=hora,
                        dia=self.normalizar_dia(str(dia)),
                    )
                    for hora in horas
                ]
            )

            self.esperar()

        return horarios
