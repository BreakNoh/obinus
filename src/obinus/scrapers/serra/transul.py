from obinus.core.base import Raspador
from obinus.core.modelos import Linha, Horario
from obinus.utils.http import get_soup, extrair_texto

URL_LINHAS = "https://transullages.com.br/linhas"
SELETOR_LINHAS = "tbody > tr"
SELETOR_NOME = "td:first-child > a"
SELETOR_CODIGO = "td:nth-child(2)"

URL_HORARIOS = "https://transullages.com.br/linha/{}/{}"
SELETOR_DIA = '[role="tablist"]'
SELETOR_DIA_UTIL = '[id="home-tab-pane"] .row > .col'
SELETOR_DIA_SAB = '[id="profile-tab-pane"] .row > .col'
SELETOR_DIA_DOM = '[id="contact-tab-pane"] .row > .col'
SELETOR_SENTIDO = "h6"
SELETOR_HORARIOS = "h6 + div"  # horarios vem num bloco só


class Transul(Raspador):
    NOME_EMPRESA = "TRANSUL"

    def raspar_linhas(self) -> list[Linha]:
        return super().raspar_linhas()

    def raspar_horarios_linha(self, linha: Linha) -> list[Horario]:
        return super().raspar_horarios_linha(linha)
