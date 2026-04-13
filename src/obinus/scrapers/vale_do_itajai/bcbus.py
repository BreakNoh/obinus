import re
from obinus.core import *
from bs4 import BeautifulSoup
from obinus.utils.http import get_soup, extrair_texto

URL: str = "https://bcbus.com.br/"


class BCBus(InterfaceRaspador[Html, Html, Html]):
    def empresa(self) -> Empresa:
        return Empresa(id="bcbus", nome="BCBus", regioes=VALE_DO_ITAJAI)

    def buscar_linhas(self) -> Html:
        return Html(get_soup(URL))

    def buscar_horarios(self, busca: Html) -> Html:
        return busca

    def extrair_linhas(self, payload: Html) -> list[tuple[Linha, Html]]:
        linhas: dict[str, tuple[Linha, BeautifulSoup]] = {}

        for info in payload.html.select("div.et_pb_equal_columns"):
            if nome := extrair_texto(info.select_one("div:first-child h3 span")):
                if not nome in linhas:
                    linhas[nome] = (Linha(nome), BeautifulSoup())

                linhas[nome][1].append(info)

        linhas_final = []
        [linhas_final.append((l, Html(h))) for l, h in linhas.values()]

        return linhas_final

    def extrair_horarios(self, payload: Html) -> list[Servico]:
        TODOS_DIAS = DIAS_UTEIS | SABADO | DOMINGO_E_FERIADOS
        DIAS = {
            "SEGUNDA A SEXTA": DIAS_UTEIS,
            "DIAS DE SEMANA": DIAS_UTEIS,
            "SÁBADOS": SABADO,
            "DOMINGOS E FERIADOS": DOMINGO_E_FERIADOS,
            "SÁB E DOM": SABADO | DOMINGO_E_FERIADOS,
            "DIARIAMENTE": TODOS_DIAS,
            "TODOS OS DIAS": TODOS_DIAS,
        }
        PADRAO_HORARIO = re.compile(r"(?P<hor>\d{2}h\d{2})(?:\W)*(?P<obs>[^)]*)?")

        servicos = []
        sub_sentido = False

        for coluna in payload.html.select("div.et_pb_equal_columns"):
            sentido = extrair_texto(
                coluna.select_one("div:first-child h2")
            )  # primeiro ve se sentido está embaixo do nome da linha

            for sub_col in coluna.select("div + div"):
                if not (dia := extrair_texto(sub_col.select_one("h3:first-child"))):
                    continue

                if (not sentido or sub_sentido) and (
                    sentido_novo := extrair_texto(sub_col.select_one("h3 + h3"))
                ):  # caso sentido esteja abaixo do dia
                    sentido = sentido_novo
                    sub_sentido = True
                elif not sentido:
                    sub_sentido = False
                    continue

                servico = Servico(DIAS[dia.upper().strip()], sentido)

                for item in sub_col.select("li"):
                    if (texto := extrair_texto(item)) and (
                        match := PADRAO_HORARIO.search(texto)
                    ):
                        horario = Horario(match.group("hor").replace("h", ":"))
                        obs_raw = match.group("obs")

                        if "DEZ" in obs_raw:
                            horario.obs.append(PeriodoFuncionamento(obs_raw))
                        elif obs_raw != "":
                            horario.obs.append(ItinerarioDiferenciado(obs_raw))

                        servico.horarios.append(horario)

                servicos.append(servico)

        return servicos
