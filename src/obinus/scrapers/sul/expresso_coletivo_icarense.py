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
        SELETOR_PAGINA_DIA = "div.e-n-tabs-content > div.elementor-element"
        SELEROT_NOME_LINHA = ".fa-bus-alt + div"
        DIAS = ["DU", "SAB", "DOM"]

        linhas: dict[str, BeautifulSoup] = {}

        for i, tab_dia in enumerate(payload.html.select(SELETOR_PAGINA_DIA)):
            if not (blocos := tab_dia.find(class_="jet-listing-grid__items")):
                continue

            for bloco in blocos.find_all(
                class_="jet-listing-grid__item",
                recursive=False,  # pega só os filhos imediatos
            ):
                if nome := extrair_texto(bloco.select_one(SELEROT_NOME_LINHA)):
                    if not nome in linhas:
                        linhas[nome] = BeautifulSoup()

                    bloco["data-dia"] = DIAS[i]
                    linhas[nome].append(bloco)

        linhas_final = []
        [
            linhas_final.append((Linha(nome), Html(html)))
            for nome, html in linhas.items()
        ]

        return linhas_final

    def extrair_horarios(self, payload: Html) -> list[Servico]:
        DIAS = {"DU": DIAS_UTEIS, "SAB": SABADO, "DOM": DOMINGO_E_FERIADOS}
        servicos = []

        for bloco in payload.html.find_all(
            class_="jet-listing-grid__item",
            recursive=False,  # pega só os filhos imediatos
        ):
            if id_dia := bloco.get("data-dia"):
                dia = DIAS[str(id_dia).upper()]
            else:
                continue

            hora, via = [
                extrair_texto(t)
                for t in bloco.select(".jet-listing-dynamic-field__content", limit=2)
            ]

            if not hora or not via:
                continue

            servico = Servico(dia)

            servico.horarios.append(
                Horario(hora, [ItinerarioDiferenciado(f"Via {via}")])
            )

        return servicos
