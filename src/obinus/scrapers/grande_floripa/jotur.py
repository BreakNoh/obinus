import re
from bs4 import BeautifulSoup
from obinus.core.raspador import InterfaceRaspador
from obinus.core.tipos import *
from obinus.utils.http import get_soup, extrair_texto

EMPRESA: str = "JOTUR"

URL_BASE = "https://www2.jotur.com.br/linhas"
DIAS = {
    "Dias Úteis": DIAS_UTEIS,
    "Sábados": SABADO,
    "Domingos e Feriados": DOMINGO_E_FERIADOS,
}


class Jotur(InterfaceRaspador[Html, Html, Url]):
    def empresa(self) -> Empresa:
        return Empresa(
            id="jotur", nome="Jotur", regioes=GRANDE_FLORIPA, fonte="https://www2.jotur.com.br"
        )

    def buscar_linhas(self) -> Html:
        html_final = BeautifulSoup()
        html = get_soup(URL_BASE)

        [html_final.append(link) for link in html.select("ul a")]

        return Html(html_final)

    def extrair_linhas(self, payload: Html) -> list[tuple[Linha, Url]]:
        linhas = []
        PADRAO_NOME_DETELHE = re.compile(
            r"^\W*(?P<nome>.+?)\s*(?P<detalhe>via.+?)?\W*$", re.IGNORECASE
        )

        for item in payload.html.select("a"):
            url = f"{URL_BASE}/{item['href']}"

            if (cod := extrair_texto(item.select_one("strong, b"))) and (
                nome := extrair_texto(item.find("span"))
            ):
                tipo = (
                    TipoLinha.EXECUTIVO
                    if "executivo" in nome.lower()
                    else TipoLinha.CONVENCIONAL
                )

                if match := PADRAO_NOME_DETELHE.search(nome):
                    nome_limpo = match.group("nome")
                    detalhe = match.group("detalhe")
                else:
                    nome_limpo = nome
                    detalhe = None

                linha = Linha(nome=nome_limpo, detalhe=detalhe, codigo=cod, tipo=tipo)

                linhas.append((linha, Url(url)))

        return linhas

    def buscar_horarios(self, busca: Url) -> Html:
        html_final = BeautifulSoup()
        html = get_soup(busca.url)

        for aba in html.select(".accordion-item"):
            if sentido := extrair_texto(
                aba.select_one(".accordion-header > span:last-child")
            ):
                for coluna in aba.select(".column"):
                    coluna["data-sentido"] = sentido
                    html_final.append(coluna)

        return Html(html_final)

    def extrair_horarios(self, payload: Html) -> list[Servico]:
        servicos = []

        for coluna in payload.html.select("div.column[data-sentido]"):
            if dia := extrair_texto(coluna.select_one("h4")):
                sentido = str(coluna["data-sentido"])
                servico = Servico(DIAS[dia], sentido)
            else:
                continue

            for item in coluna.select("div.time-item"):
                if hora := extrair_texto(item):
                    servico.horarios.append(Horario(hora))

            servicos.append(servico)

        return servicos
