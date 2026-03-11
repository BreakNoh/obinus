from common import *

EMPRESA: str = "BIGUACU"

URL_BASE = "https://www.tcbiguacu.com.br"
URL_BUSCA_LINHAS = URL_BASE + "/sistema/sys/AJAX_search_line.php"
URL_HORARIOS = URL_BASE + "/sistema/sys/AJAX_get_line_hours.php"


PATAMARES: dict = {"EXECUTIVO": "5", "CONVECIONAL": "0"}


def raspar_linhas_patamar(patamar: str) -> list[Linha]:
    linhas = []
    if not patamar in PATAMARES.keys():
        return linhas

    soup, status = get_soup(URL_BUSCA_LINHAS, {"id_grupo_bus": PATAMARES[patamar]})

    for li in soup.select("li"):
        codigo = extrair_texto(li.select_one(".code-line"))
        nome = extrair_texto(li.select_one(".name-line"))
        detalhe = extrair_texto(li.select_one("span"))
        url = f"{URL_HORARIOS}?id_line_bus={codigo}"
        executivo = patamar == "EXECUTIVO"

        linhas.append(Linha(EMPRESA, codigo, nome, detalhe, executivo, url))

    return linhas


DIAS: dict[str, str] = {"UTIL": "1", "SABADO": "2", "DOMINGO_FERIADO": "3"}


def raspar_horarios_dia(linha: Linha, dia: str, id_dia: str) -> list[Horario]:
    soup, _ = get_soup(linha.url, {"id_day_week": id_dia})
    horarios = []
    codigo = linha.codigo

    for s in soup.select(".hours-line"):
        sentido = extrair_texto(s.select_one(".title"))

        if sentido == "":
            continue

        for h in s.select(".hour"):
            hora = extrair_texto(h)

            horarios.append(Horario(EMPRESA, codigo, sentido, hora, dia))

    return horarios


class Biguacu(Raspador):
    def empresa(self) -> str:
        return EMPRESA

    def raspar_linhas(self) -> list[Linha]:
        linhas = []

        for pat in PATAMARES.keys():
            linhas.extend(raspar_linhas_patamar(pat))

        return linhas

    def raspar_horarios_linha(self, linha: Linha) -> list[Horario]:
        horarios = []

        for dia, id_dia in DIAS.items():
            horarios.extend(raspar_horarios_dia(linha, dia, id_dia))

        return horarios
