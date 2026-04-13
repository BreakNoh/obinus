from obinus.utils.http import get_soup
from obinus.utils.texto import extrair_texto
from obinus.core.raspador import InterfaceRaspador
from obinus.core.tipos import *

EMPRESA: str = "BIGUACU"

URL_BASE = "https://www.tcbiguacu.com.br"
URL_BUSCA_LINHAS = "https://www.tcbiguacu.com.br/sistema/sys/AJAX_search_line.php"
URL_LINHAS = "https://www.tcbiguacu.com.br/sistema/sys/AJAX_search_line.php"
URL_HORARIOS = "https://www.tcbiguacu.com.br/sistema/sys/AJAX_get_line_hours.php"

DIAS: dict[str, Dias] = {"1": DIAS_UTEIS, "2": SABADO, "3": DOMINGO_E_FERIADOS}


class TCBiguacu(InterfaceRaspador[Html, Html, Raw]):
    def empresa(self) -> Empresa:
        return Empresa(
            id="transporte-coletivo-biguacu",
            nome="Transporte Coletivo Biguaçu",
            regioes=GRANDE_FLORIPA,
        )

    def extrair_linhas(self, payload: Html) -> list[tuple[Linha, Raw]]:
        linhas = []

        for item in payload.html.select("li"):
            codigo = extrair_texto(item.select_one(".code-line"))
            nome = extrair_texto(item.select_one(".name-line"))
            detalhe = extrair_texto(item.select_one("span"))
            tipo = (
                TipoLinha.EXECUTIVO
                if item.has_attr("data-exec")
                else TipoLinha.CONVENCIONAL
            )

            linhas.append(
                (
                    Linha(nome=nome, codigo=codigo, tipo=tipo, detalhe=detalhe),
                    Raw(codigo),
                )
            )

        return linhas

    def extrair_horarios(self, payload: Html) -> list[Servico]:
        servicos = []

        for serv in payload.html.select(".hours-line"):
            sentido = extrair_texto(serv.select_one(".title"))
            dia = DIAS[str(serv.get("data-dia"))] or 0
            servico = Servico(dias=dia, sentido=sentido)

            for h in serv.select("ul > li"):
                horario: Horario | None = None

                if hora := extrair_texto(h.select_one(".hour")):
                    horario = Horario(hora)

                if not horario:
                    continue

                for ico in h.select(".ico"):
                    if "adaptado" in ico["class"]:
                        horario.obs.append(Adaptado())
                    if "itinerario" in ico["class"]:
                        legenda = extrair_texto(h.select_one(".leg_dif"))
                        horario.obs.append(ItinerarioDiferenciado(legenda))
                    if "compartilhada" in ico["class"]:
                        horario.obs.append(OperadoPor("Biguaçu"))
                    if "ponto-final" in ico["class"]:
                        horario.obs.append(RecolheBairro())

                servico.horarios.append(horario)

            servicos.append(servico)

        return servicos

    def buscar_horarios(self, busca: Raw) -> Html:
        html_final = BeautifulSoup()

        for i in "123":  # uma requisição para cada dia
            self._esperar()
            html = get_soup(
                URL_HORARIOS, params={"id_line_bus": busca.valor, "id_day_week": i}
            )
            for j in html.select(".hours-line"):  # anota o dia
                j["data-dia"] = i
                html_final.append(j)

        return Html(html_final)

    def buscar_linhas(self) -> Html:
        html_final = BeautifulSoup()

        for tipo, id in [("conv", "0"), ("exec", "5")]:
            html = get_soup(URL_LINHAS, params={"id_grupo_bus": id})

            for item in html.select("li"):
                item[f"data-{tipo}"] = ""
                html_final.append(item)

        return Html(html_final)  # html transformado e anotado
