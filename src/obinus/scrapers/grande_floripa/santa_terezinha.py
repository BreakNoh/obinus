from obinus.core.raspador import InterfaceRaspador
from obinus.core.tipos import *
from obinus.utils.http import get_soup, extrair_texto
import re

URL_BASE = "https://santaterezinha.com/horarios"
TRADUCAO = str.maketrans(
    {
        "á": "a",
        "ã": "a",
        "â": "a",
        "à": "a",
        "ó": "o",
        "õ": "o",
        "ô": "o",
        "é": "e",
        "í": "i",
        "ú": "u",
        " ": "-",
        "ç": "c",
    }
)
DIAS = {
    "SEGUNDA A SEXTA": DIAS_UTEIS,
    "SÁBADO": SABADO,
    "DOMINGOS E FERIADOS": DOMINGO_E_FERIADOS,
}
SEPARADORES = re.compile(r"[\-\u2013\u2014]")


class SantaTerezinha(InterfaceRaspador[Html, Html, Url]):
    def empresa(self) -> Empresa:
        return Empresa(nome="Santa Terezinha", regioes=GRANDE_FLORIPA)

    def buscar_linhas(self) -> Html:
        html_final = BeautifulSoup()

        for item in get_soup(URL_BASE).select(".box-body"):
            html_final.append(item)

        return Html(html_final)

    def buscar_horarios(self, busca: Url) -> Html:
        html = get_soup(busca.url)
        html_final = BeautifulSoup()

        for legenda in html.select(".dialog-message p"):
            legenda["data-legenda"] = ""
            html.append(legenda)

        for bloco in html.find_all("details"):
            html_final.append(bloco)

        return Html(html)

    def gerar_url(self, nome_linha: str) -> str:
        nome_normalizado = nome_linha.lower().translate(TRADUCAO)
        return f"{URL_BASE}/{nome_normalizado}"

    def extrair_linhas(self, payload: Html) -> list[tuple[Linha, Url]]:
        linhas = []

        for item in payload.html.select(".box-body"):
            nome = extrair_texto(item.select_one("h3"))

            if not nome:
                continue

            if link := item.select_one("a"):
                url = link.get("href")
            else:
                url = self.gerar_url(nome)

            linha = Linha(nome)

            linhas.append((linha, url))

        return linhas

    def extrair_legenda(
        self, html: BeautifulSoup | Tag
    ) -> list[tuple[str, ObsHorario]]:
        legendas = []

        for item in html.select("[data-legenda]"):
            if cod := item.find("strong"):
                codigo = extrair_texto(cod)
                valor = extrair_texto(item)

                if codigo and valor:
                    valor = SEPARADORES.sub("", valor).strip()
                    codigo = codigo.strip()
            elif conteudo := extrair_texto(item):
                codigo, valor = SEPARADORES.split(conteudo, maxsplit=1)

                if codigo and valor:
                    valor = SEPARADORES.sub("", valor).strip()
                    codigo = codigo.strip()
            else:
                continue
            if not valor or not codigo:
                continue

            if re.search(r"adptado|necessidades especiais", valor.lower()):
                obs = Adaptado()
            elif re.search(r"via|linha", valor.lower()):
                obs = ItinerarioDiferenciado(valor)
            elif re.search(r"estrela|terezinha|biguaçú", valor.lower()):
                obs = OperadoPor(valor.replace("ú", "u"))
            elif re.search(r"sai|saem", valor.lower()):
                obs = SaidaDe(valor)
            else:
                obs = Generica(valor=valor)

            legendas.append((f"{codigo: >2}", obs))

        return legendas

    def adicionar_obs(
        self, horario: Horario, texto: str, legendas: list[tuple[str, ObsHorario]]
    ):
        for item in legendas:
            if item[0] in texto:
                horario.obs.append(item[1])

    def extrair_horarios(self, payload: Html) -> list[Servico]:
        servicos = []
        legendas = self.extrair_legenda(payload.html)

        for tag_s in payload.html.find_all("details"):
            sentido = extrair_texto(tag_s.select_one(".e-n-accordion-item-title-text"))
            if not sentido:
                continue
            servico = Servico(sentido=sentido)

            for col in tag_s.select(".e-con-inner"):
                dia = extrair_texto(col.select_one("h2"))

                if dia:
                    servico.dias = DIAS[dia.upper()] or 0
                else:
                    continue

                for item in col.select(".elementor-icon-list-text"):
                    conteudo = extrair_texto(item)
                    if not conteudo:
                        continue

                    horario = None

                    if match := re.search("[0-9]+:[0-9]+", conteudo):
                        horario = Horario(match.group())
                        self.adicionar_obs(horario, conteudo, legendas)
                    else:
                        continue

                    servico.horarios.append(horario)

                servicos.append(servico)

        return servicos
