import re
from obinus.core.raspador import InterfaceRaspador
from obinus.core.tipos import *
from obinus.utils.http import get_soup, extrair_texto


URL_LINHAS = "https://www.tcimperatriz.com.br/horarios"
DIAS = {
    "dia-1": DIAS_UTEIS,
    "dia-2": SABADO,
    "dia-3": DOMINGO_E_FERIADOS,
}


class TCImperatriz(InterfaceRaspador[Html, Html, Url]):
    def buscar_linhas(self) -> Html:
        html_final = BeautifulSoup()

        for item in get_soup(URL_LINHAS).select(".elementor-shortcode  li > a"):
            item["data-linha"] = ""
            html_final.append(item)

        return Html(html_final)

    def extrair_linhas(self, payload: Html) -> list[tuple[Linha, Url]]:
        linhas = []

        for item in payload.html.select("a[data-linha]"):
            nome = extrair_texto(item.select_one("b"))

            if texto := extrair_texto(item):
                if texto.count("-") == 2:
                    codigo, detalhe = re.split(r"-.*-", texto, maxsplit=1)
                else:
                    codigo = texto.replace("-", "").strip()
                    detalhe = None
            else:
                codigo = None
                detalhe = None

            if not nome or not codigo:
                continue

            url = str(item["href"])
            linhas.append((Linha(nome, codigo, detalhe), Url(url)))

        return linhas

    def buscar_horarios(self, busca: Url) -> Html:
        html_final = BeautifulSoup()
        html = get_soup(busca.url)

        for botao in html.select("button[id^=dia]"):
            if item := html.select_one(f".diapanel#{botao['aria-controls']}"):
                item["data-dia"] = botao["id"]
                html_final.append(item)

        return Html(html_final)

    def extrair_horarios(self, payload: Html) -> list[Servico]:
        servicos = []

        for painel in payload.html.select("div.diapanel[data-dia]"):
            dia = DIAS[str(painel["data-dia"])] or 0

            for sub in painel.select(".horario--panel"):
                sentido = extrair_texto(sub.select_one("h3"))
                if sentido == "":
                    continue

                servico = Servico(dia, sentido)

                for item in sub.select("li"):
                    if (texto := extrair_texto(item)) and (
                        match := re.search(r"\d{2}:\d{2}", texto)
                    ):
                        hora = match.group()
                    else:
                        continue
                    if texto := extrair_texto(item.find("span")):
                        obs = Generica(valor=texto)
                    else:
                        obs = None

                    servico.horarios.append(Horario(hora, obs=[obs] if obs else []))

                servicos.append(servico)

        return servicos
