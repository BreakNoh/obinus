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


class SantaTerezinha(InterfaceRaspador[Html, Html, Url]):
    def buscar_linhas(self) -> Html:
        return Html(get_soup(URL_BASE))

    def buscar_horarios(self, busca: Url) -> Html:
        html = get_soup(busca.url)
        if "diretao" in busca.url and (root := html.find("html")):
            root["data-diretao"] = ""
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

            url = item.get("href") or self.gerar_url(nome)

            linha = Linha(nome)

            linhas.append((linha, url))

        return linhas

    def adicionar_obs(self, horario: Horario, texto: str, linha_comp: bool = False):
        tabela = [
            ("GV", SaidaDe("Residencial Garden Ville")),
            ("SE", ItinerarioDiferenciado("Da linha Sertão do Maruim")),
            [
                ("EXP BR", ItinerarioDiferenciado("Via Via Expressa e BR101")),
                ("EXP", ItinerarioDiferenciado("Via Via Expressa")),
            ],
            ("PE", Generica(valor="Período Escolar")),
            [
                (
                    "SC*",
                    ItinerarioDiferenciado(
                        "Rua Luiz Fagundes até Armazem Vieira (Via Shopping Continente)"
                    ),
                ),
                ("SC", ItinerarioDiferenciado("Via Shopping Continente")),
            ],
            (" A", ItinerarioDiferenciado("Via Aero Club")),
            ("UN", ItinerarioDiferenciado("Via Univali")),
            (" B", Generica(valor="Sai do condomínio Beija Flor")),
            ("LV", ItinerarioDiferenciado("Via Lagoa Vermelha")),
            ("VJ", ItinerarioDiferenciado("Via Vila Junkes")),
            ("SD", Generica(valor="Entra no residencial Santos Drummont")),
            (" D", Adaptado()),
            ("VP", Generica(valor="Sai do condomínio Vila do Porto")),
        ]
        ext_tabela = [
            ("ST", OperadoPor("Santa Terezinha")),
            (" E", OperadoPor("Estrela")),
            (" B", OperadoPor("Biguaçu")),
        ]

        alvo = tabela if not linha_comp else ext_tabela
        for item in alvo:
            if not isinstance(item, list):
                if item[0] in texto:
                    horario.obs.append(item[1])
            else:
                for sub in item:
                    if sub[0] in texto:
                        horario.obs.append(sub[1])
                        break

    def extrair_horarios(self, payload: Html) -> list[Servico]:
        servicos = []
        linha_comp = False
        if (root := payload.html.find("html")) and root.has_attr("data-diretao"):
            linha_comp = True

        for tag_s in payload.html.select("details"):
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
                        self.adicionar_obs(horario, conteudo, linha_comp)
                    else:
                        continue

                    servico.horarios.append(horario)

                servicos.append(servico)

        return servicos
