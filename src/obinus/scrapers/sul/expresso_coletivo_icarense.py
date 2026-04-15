from bs4 import BeautifulSoup
from obinus.core import *
from obinus.utils.http import get_soup, extrair_texto
from obinus.utils.texto import normalizar_dia

URL = "https://icarense.com.br/linhas-e-horarios/"


class ExpressoColetivoIcarense(InterfaceRaspador[Html, Html, Html]):
    def empresa(self) -> Empresa:
        return Empresa(
            id="expresso-coletivo-icarense",
            nome="Expresso Coletivo Içarense",
            regioes=SUL,
            fonte="https://icarense.com.br",
        )

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

        linhas: dict[str, tuple[str, BeautifulSoup]] = {}

        for pag in payload.html.select(SELETOR_PAGINA_DIA):
            for bloco in pag.select(SELETOR_BLOCOS):
                if nome_linha := extrair_texto(bloco.select_one(SELETOR_NOME_LINHA)):
                    tabela_horarios = bloco.select_one(SELETOR_TABELA_HORARIOS)
                    dia = ID_DIAS.get(str(pag["id"]).lower())
                    if not dia or not tabela_horarios:
                        continue

                    tokens = nome_linha.strip().split(" ")
                    tabela_horarios["data-sentido"] = tokens[0]
                    tabela_horarios["data-dia"] = dia

                    nome_comp = "".join(sorted(tokens))

                    if not nome_comp in linhas.keys():
                        linhas[nome_comp] = (nome_linha, BeautifulSoup())

                    linhas[nome_comp][1].append(tabela_horarios)  # adicionar no html

        return [(Linha(nom), Html(htm)) for nom, htm in linhas.values()]

    def extrair_horarios(self, payload: Html) -> list[Servico]:
        SELETOR_ROWS = "div.jet-listing-grid__item[data-post-id]:not([data-listing-source]) div.e-con-inner"

        servicos = []

        for tabela_dia in payload.html.select("div[data-dia][data-sentido]"):
            dia = normalizar_dia(str(tabela_dia["data-dia"]))
            sentido = str(tabela_dia["data-sentido"])

            servico = Servico(dia, sentido)

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
