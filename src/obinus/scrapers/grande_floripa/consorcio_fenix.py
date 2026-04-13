import re

from obinus.utils.http import get_soup
from obinus.utils.texto import extrair_texto

from obinus.core.raspador import InterfaceRaspador
from obinus.core.tipos import *


EMPRESA: str = "FENIX"

URL_LINHAS = "https://www.consorciofenix.com.br/horarios"
URL_BASE = "https://www.consorciofenix.com.br"

DIAS = {}


def parsear_dias(d: str) -> Dias:
    match d.lower():
        case "dias úteis":
            return DIAS_UTEIS
        case "sábado":
            return SABADO
        case "domingos e feriados":
            return DOMINGO_E_FERIADOS
        case _:
            return 0


class ConsorcioFenix(InterfaceRaspador[Html, Html, Url]):
    def empresa(self) -> Empresa:
        return Empresa(id="consorcio-fenix", nome="Consórcio Fênix", regioes=GRANDE_FLORIPA)

    def extrair_linhas(self, payload: Html) -> list[tuple[Linha, Url]]:
        linhas = []

        for item in payload.html.select(".wrap-horarios li a"):
            conteudo = extrair_texto(item)

            [codigo, nome] = re.split(r"\s+-\s+", conteudo, maxsplit=1)

            executivo = "executivo" in nome.lower()
            codigo = codigo.strip()
            nome = nome.strip()
            url = URL_BASE + str(item.get("href"))

            linha = Linha(nome=nome, codigo=codigo)
            if executivo:
                linha.tipo = TipoLinha.EXECUTIVO

            linhas.append((linha, Url(url)))

        return linhas

    def extrair_horarios(self, payload: Html) -> list[Servico]:
        servicos: list[Servico] = []
        servico_atual: Servico | None = None

        for sub in payload.html.select(".my-subtab-content"):
            sentido = extrair_texto(sub.select_one("h5"))
            servico_atual = None

            for horario in sub.select("div[data-semana][data-horario]"):
                if (d := horario.get("data-semana")) and not servico_atual:
                    servico_atual = Servico(dias=parsear_dias(str(d)), sentido=sentido)

                hor: None | Horario = None

                if not servico_atual:
                    continue

                if hora := horario.get("data-horario"):  # extrai horario
                    hor = Horario(str(hora))

                if not hor:
                    continue

                if obs := extrair_texto(
                    horario.find("b")
                ):  # extrair info sobre o horario
                    for ch in obs.lower().replace(" ", ""):
                        match ch:
                            case "e":
                                hor.obs.append(Adaptado())
                            case "m":
                                hor.obs.append(MeiaViagem())
                            case "*":
                                hor.obs.append(HorarioPrevisto())

                servico_atual.horarios.append(hor)

            if servico_atual:
                servicos.append(servico_atual)

        return servicos

    def buscar_linhas(self) -> Html:
        return Html(get_soup(URL_LINHAS))

    def buscar_horarios(self, busca: Url) -> Html:
        return Html(get_soup(busca.url))
