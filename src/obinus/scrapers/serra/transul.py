from obinus.core import Raspador, Linha, Horario
from obinus.utils import get_soup, extrair_texto

URL_LINHAS = "https://transullages.com.br/linhas"
SELETOR_LINHAS = "tbody > tr"
SELETOR_NOME = "td:first-child > a"
SELETOR_CODIGO = "td:nth-child(2)"

SELETOR_DIA = '[role="tablist"]'
SELETOR_DIA_UTIL = '[id="home-tab-pane"] .row > .col'
SELETOR_DIA_SAB = '[id="profile-tab-pane"] .row > .col'
SELETOR_DIA_DOM = '[id="contact-tab-pane"] .row > .col'
SELETOR_SENTIDO = "h6"
SELETOR_HORARIOS = "h6 + div"  # horarios vem num bloco só


class Transul(Raspador):
    NOME_EMPRESA = "TRANSUL"

    def raspar_linhas(self) -> list[Linha]:
        soup, _ = get_soup(URL_LINHAS)
        linhas = []

        for lin in soup.select(SELETOR_LINHAS):
            nome = extrair_texto(lin.select_one(SELETOR_NOME))
            codigo = extrair_texto(lin.select_one(SELETOR_CODIGO))
            url: str | None = None

            if tag := lin.select_one(SELETOR_NOME):
                url = str(tag.get("href"))

            if not nome or not codigo:
                continue

            linhas.append(
                Linha(
                    empresa=self.NOME_EMPRESA, codigo=codigo, nome=nome, url=url or ""
                )
            )

        return linhas

    def raspar_horarios_linha(self, linha: Linha) -> list[Horario]:
        return super().raspar_horarios_linha(linha)
