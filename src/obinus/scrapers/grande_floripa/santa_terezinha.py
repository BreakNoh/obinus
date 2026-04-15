from obinus.core.raspador import InterfaceRaspador
from obinus.core.tipos import *
from obinus.utils.http import get_soup, extrair_texto
import re

from obinus.utils.texto import normalizar_dia

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
        return Empresa(
            id="santa-terezinha",
            nome="Santa Terezinha",
            regioes=GRANDE_FLORIPA,
            fonte="https://santaterezinha.com",
        )

    def buscar_linhas(self) -> Html:
        html_final = BeautifulSoup()

        for item in get_soup(URL_BASE).select(".box-body"):
            html_final.append(item)

        return Html(html_final)

    def buscar_horarios(self, busca: Url) -> Html:
        SELETOR_ITEM_LEGENDA = "div[data-elementor-type=popup] p"
        html = get_soup(busca.url)
        html_final = BeautifulSoup()

        for bloco in html.find_all("details"):
            html_final.append(bloco)

        for legenda in html.select(SELETOR_ITEM_LEGENDA):
            legenda["data-legenda"] = ""

            html_final.append(legenda)

        return Html(html_final)

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
                url = link.get("href") or self.gerar_url(nome)
            else:
                url = self.gerar_url(nome)

            linha = Linha(nome)

            linhas.append((linha, Url(str(url))))

        return linhas

    def extrair_legenda(self, html: BeautifulSoup | Tag) -> dict[str, ObsHorario]:
        legendas = {}

        for item in html.select("[data-legenda]"):
            if cod := item.find("strong"):
                codigo = extrair_texto(cod)
                valor = extrair_texto(item)

                if codigo and valor:
                    valor = SEPARADORES.sub("", valor).strip()
                    codigo = codigo.strip()

            elif conteudo := extrair_texto(item):
                try:
                    codigo, valor = SEPARADORES.split(conteudo, maxsplit=1)

                    if codigo and valor:
                        valor = SEPARADORES.sub("", valor).strip()
                        codigo = codigo.strip()
                except:
                    continue
            else:
                continue
            if not valor or not codigo:
                continue

            if re.search(r"adptado|necessidades especiais", valor.lower()):
                obs = Adaptado()
            elif re.search(r"via|linha", valor.lower()):
                obs = ItinerarioDiferenciado(valor)
            elif re.search(r"estrela|terezinha|biguaçú", valor.lower()):
                obs = OperadoPorEmpresa(valor.replace("ú", "u"))
            elif re.search(r"sai|saem", valor.lower()):
                obs = SaidaDe(valor)
            else:
                obs = Generica(valor=valor)

            legendas[f"{codigo: >2}"] = obs

        return legendas

    def adicionar_obs(
        self, horario: Horario, texto: str, legendas: dict[str, ObsHorario]
    ):
        for cod, leg in legendas.items():
            if cod in texto:
                horario.obs.append(leg)

    def extrair_horarios(self, payload: Html) -> list[Servico]:
        SELETOR_BLOCO_SENTIDO = "details"
        SELETOR_SENTIDO = "div.e-n-accordion-item-title-text"
        SELETOR_DIA = "summary + div > div"

        servicos = []
        legendas = self.extrair_legenda(payload.html)

        for tag_s in payload.html.select(SELETOR_BLOCO_SENTIDO):
            if not (sentido := extrair_texto(tag_s.select_one(SELETOR_SENTIDO))):
                continue

            servico = Servico(sentido=sentido)

            for col in tag_s.select(SELETOR_DIA):
                if not (dia := extrair_texto(col.select_one("h2"))):
                    continue

                servico.dias = normalizar_dia(dia)

                for item in col.select(".elementor-icon-list-text"):
                    conteudo = extrair_texto(item)

                    if not conteudo:
                        continue

                    horario = None

                    if match := re.search(r"\d{1,2}:\d{1,2}", conteudo):
                        horario = Horario(match.group())
                        self.adicionar_obs(horario, conteudo, legendas)
                    else:
                        continue

                    servico.horarios.append(horario)

                servicos.append(servico)

        return servicos
