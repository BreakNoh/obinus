import re
from obinus.core.tipos import *
from obinus.core.raspador import InterfaceRaspador
from obinus.utils.http import get_soup
from obinus.utils.texto import extrair_texto

URL_BASE = "https://insulartc.com.br"
URL_LINHAS = f"{URL_BASE}/est/wp/"


class TCEstrela(InterfaceRaspador[Html, Html, Url]):
    def buscar_linhas(self) -> Html:
        return Html(get_soup(URL_LINHAS))

    def extrair_linhas(self, payload: Html) -> list[tuple[Linha, Url]]:
        linhas = []

        for lin in payload.html.find_all("tr"):
            if (
                (cod := extrair_texto(lin.select_one("td:first-child")))
                and (tag := lin.select_one("a"))
                and (nome := extrair_texto(tag))
            ):
                tipo = (
                    TipoLinha.EXECUTIVO
                    if re.search(r"executivo|vip", nome.lower())
                    else TipoLinha.CONVENCIONAL
                )

                url = str(tag["href"])

                linhas.append((Linha(nome, cod, tipo=tipo), Url(url)))

        return linhas

    def buscar_horarios(self, busca: Url) -> Html:
        return Html(get_soup(busca.url))

    def extrair_legenda(
        self, html: BeautifulSoup | Tag
    ) -> list[tuple[str, ObsHorario]]:
        legenda = []
        dentro_legenda = False
        PADRAO = re.compile(r"(?P<cod>[\*A-Z\u00B2\u00B9]+?)(?:\W+)(?P<leg>.*)")

        for lin in html.find_all("tr"):
            cols = lin.find_all("td")

            for c in cols:
                valor = extrair_texto(c)
                valor_norm = valor.lower()

                if "observaç" in valor_norm:
                    dentro_legenda = True
                    continue
                elif not dentro_legenda:
                    continue
                elif len(cols) == 3:
                    break

                if match := PADRAO.search(valor):
                    leg = match.group("leg")
                    leg_norm = leg.lower()
                    cod = match.group("cod")

                    if cod == "*":
                        obs = HorarioPrevisto()
                    elif "recolhe" in leg_norm:
                        obs = RecolheBairro()
                    elif "até" in leg_norm:
                        obs = ItinerarioDiferenciado(leg)
                    elif cod in "\u00b2\u00b9":
                        obs = OperadoPor("Estrela", leg)
                    else:
                        obs = Generica(valor=leg)

                    legenda.append((match.group("cod"), obs))

        return legenda

    def adicionar_obs(
        self, horario: Horario, texto: str, legenda: list[tuple[str, ObsHorario]]
    ):
        for cod, obs in legenda:
            if cod in texto:
                horario.obs.append(obs)

    def extrair_horarios(self, payload: Html) -> list[Servico]:
        servicos = []
        legenda = self.extrair_legenda(payload.html)

        for lin in payload.html.find_all("tr"):
            cols = lin.find_all("td")
            buffer_sentido = None
            servicos_dias = None

            print(len(cols))
            match len(cols):
                case 3:
                    buffer_sentido = extrair_texto(cols[1])
                    continue
                case 5 | 7 if buffer_sentido:
                    print(buffer_sentido)
                    servicos_dias = [
                        Servico(DIAS_UTEIS, buffer_sentido),
                        Servico(SABADO, buffer_sentido),
                        Servico(DOMINGO_E_FERIADOS, buffer_sentido),
                    ]
                    buffer_sentido = None
                case 7 if servicos_dias:
                    print("a")
                    pass
                case _ if servicos_dias:
                    buffer_sentido = None
                    continue

            if not servicos_dias:
                continue

            for i, dia in enumerate([0, 0, 0, 1, 1, 2]):
                if (texto := extrair_texto(cols[i + 1]).strip()) and (
                    hora := re.search(r"\d{2}\.\d{2}", texto)
                ):
                    print(hora)
                    horario = Horario(hora.group().replace(".", ":"))
                    self.adicionar_obs(horario, texto, legenda)
                    servicos_dias[dia].horarios.append(horario)
                else:
                    continue

            [servicos.append(s) for s in servicos_dias]

        return servicos
