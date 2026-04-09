from bs4 import BeautifulSoup
from obinus.core import *
from obinus.utils.http import get_soup, extrair_texto

URL = "https://icarense.com.br/linhas-e-horarios/"


class ExpressoColetivoIcarense(InterfaceRaspador[Html, Html, Html]):
    def empresa(self) -> Empresa:
        return Empresa(nome="Expresso Coletivo Içarense", regioes=SUL)

    def buscar_linhas(self) -> Html:
        return Html(get_soup(URL))

    def buscar_horarios(self, busca: Html) -> Html:
        return busca

    def extrair_linhas(self, payload: Html) -> list[tuple[Linha, Html]]:
        SELETOR_PAGINA_DIA = "div[id^=listing]"
        SELETOR_BLOCOS = "div[data-query-id][data-listing-source='posts'] > div.jet-listing-grid__item[data-post-id]"
        SELETOR_NOME_LINHA = (
            ".jet-listing-dynamic-field__icon + div.jet-listing-dynamic-field__content"
        )
        SELETOR_TABELA_HORARIOS = "div[data-query-id][data-listing-source='repeater']"

        ID_DIAS = {
            "listing-dias-ulteis": "DU",  # erro de digitação proposital
            "listing-sabado": "SAB",
            "listing-domingo": "DOM",
        }

        linhas: dict[str, BeautifulSoup] = {}

        for pag in payload.html.select(SELETOR_PAGINA_DIA):
            for bloco in pag.select(SELETOR_BLOCOS):
                if nome_linha := extrair_texto(bloco.select_one(SELETOR_NOME_LINHA)):
                    tabela_horarios = bloco.select_one(SELETOR_TABELA_HORARIOS)
                    dia = ID_DIAS.get(str(pag["id"]).lower())

                    if not dia or not tabela_horarios:
                        continue

                    tabela_horarios["data-dia"] = dia

                    if not nome_linha in linhas.keys():
                        linhas[nome_linha] = BeautifulSoup()

                    linhas[nome_linha].append(tabela_horarios)

        return [(Linha(nom), Html(htm)) for nom, htm in linhas.items()]

    def extrair_horarios(self, payload: Html) -> list[Servico]:
        SELETOR_ROWS = "div.jet-listing-grid__item[data-post-id]:not([data-listing-source]) div.e-con-inner"
        DIAS = {"DU": DIAS_UTEIS, "SAB": SABADO, "DOM": DOMINGO_E_FERIADOS}

        servicos = []

        for tabela_dia in payload.html.select("div[data-dia]"):
            dia = DIAS[str(tabela_dia["data-dia"]).upper()]
            servico = Servico(dia)

            for row in tabela_dia.select(SELETOR_ROWS):
                hora, via = [
                    extrair_texto(c)
                    for c in row.select(".jet-listing-dynamic-field__content", limit=2)
                ]

                if not hora or not via:
                    continue

                servico.horarios.append(
                    Horario(hora, [ItinerarioDiferenciado(f"Via {via}")])
                )

            servicos.append(servico)

        return servicos
