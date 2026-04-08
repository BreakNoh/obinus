import re
from obinus.core import *
from obinus.utils import get_soup, extrair_texto

URL_LINHAS = "https://transullages.com.br/linhas"


class Transul(InterfaceRaspador[Html, Html, Url]):
    def empresa(self) -> Empresa:
        return Empresa(nome="Transul", regioes=SUL)

    def extrair_linhas(self, payload: Html) -> list[tuple[Linha, Url]]:
        SELETOR_LINHAS = "table > tr"
        SELETOR_CODIGO = "td:nth-child(2)"
        SELETOR_NOME = "td:first-child > a"

        linhas = []

        for lin in payload.html.select(SELETOR_LINHAS):
            if not (codigo := extrair_texto(lin.select_one(SELETOR_CODIGO))):
                continue
            if tag_nome := lin.select_one(SELETOR_NOME):
                if not (nome := extrair_texto(tag_nome)) or not (
                    url := str(tag_nome.get("href"))
                ):
                    continue
            else:
                continue

            linhas.append((Linha(nome, codigo), Url(url)))

        return linhas

    def extrair_legenda(self, elemento: Tag | None) -> None | dict[str, ObsHorario]:
        if not elemento:
            return None

        PADRAO_LEGENDA = re.compile(r"(?P<cod>[A-Z])\W*(?P<leg>.*)")
        legenda = {}

        texto = elemento.get_text("\n")

        for i in PADRAO_LEGENDA.finditer(texto):
            cod = i.group("cod")
            leg = i.group("leg")

            legenda[cod] = ItinerarioDiferenciado(leg)

        return legenda

    def adicionar_obs(
        self, horario: Horario, amostra: str | None, legenda: dict[str, ObsHorario]
    ):
        if not amostra:
            return

        if len(amostra) > 8:
            horario.obs.append(Generica(valor=amostra.strip()))
        else:
            for ch in amostra:
                if obs := legenda.get(ch):
                    horario.obs.append(obs)

    def extrair_horarios(self, payload: Html) -> list[Servico]:
        SELETOR_DIA_UTIL = '[id="home-tab-pane"]'
        SELETOR_DIA_SAB = '[id="profile-tab-pane"]'
        SELETOR_DIA_DOM = '[id="contact-tab-pane"]'

        SELETOR_COLUA = ".row > .col"
        SELETOR_SENTIDO = "h6"
        SELETOR_HORARIOS = "h6 + div"  # horarios vem num bloco só

        PADRAO_HORARIO = re.compile(r"(?P<hora>\d{1,2}:\d{1,2})[\s\-]*(?P<obs>.*)")

        dia_seletor: list[tuple[Dias, str]] = [
            (DIAS_UTEIS, SELETOR_DIA_UTIL),
            (SABADO, SELETOR_DIA_SAB),
            (DOMINGO_E_FERIADOS, SELETOR_DIA_DOM),
        ]

        servicos = []

        for dia, seletor in dia_seletor:
            if not (legenda := self.extrair_legenda(payload.html.select_one(seletor))):
                continue

            for col in payload.html.select(f"{seletor} {SELETOR_COLUA}"):
                sentido = extrair_texto(col.select_one(SELETOR_SENTIDO))
                horas = extrair_texto(col.select_one(SELETOR_HORARIOS))

                if not sentido or not horas:
                    continue

                servico = Servico(dia, sentido)

                for hora in PADRAO_HORARIO.finditer(horas):
                    horario = Horario(hora.group("hora"))
                    self.adicionar_obs(horario, hora.group("obs"), legenda)

                    servico.horarios.append(horario)

        return servicos
