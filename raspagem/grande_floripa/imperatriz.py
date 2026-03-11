from common import *


URL_BASE = "https://www.tcimperatriz.com.br"


def raspar_linhas() -> list[Linha]:
    soup, status = get_soup(URL_BASE + "/horarios/")

    linhas = []

    for item in soup.select(".elementor-shortcode  li > a"):
        nome = extrair_texto(item.select_one("b"))
        texto = extrair_texto(item).replace("-", "")
        url = item["href"]

        codigo, detalhe = "", ""

        partes = re.split(r"\s{2,}", texto)

        if len(partes) > 0:
            codigo = partes[0].strip()
        if len(partes) > 1:
            detalhe = partes[1].strip()

        if len(nome) == 0 or len(codigo) == 0:
            continue

        linha = Linha(codigo, nome, detalhe, False, str(url))

        linhas.append(linha)

    return linhas


DIAS = {
    "Dias Úteis": "UTIL",
    "Sábado": "SABADO",
    "Domingo e Feriado": "DOMINGO_FERIADO",
}


def raspar_horarios_linha(linha: Linha) -> list[Horario]:
    soup, status = get_soup(linha.url)

    horarios = []

    for painel in soup.select(".diapanel"):
        id_botao = painel["aria-labelledby"]
        dia = extrair_texto(soup.select_one(f"#{id_botao}"))

        if not dia in DIAS.keys():
            continue

        dia = DIAS[dia]

        for sub in painel.select(".horario--panel"):
            sentido = extrair_texto(sub.select_one("h3"))
            if sentido == "":
                continue
            for item in sub.select("li"):
                hora = extrair_texto(item)
                hora_extraida = re.search(r"[0-9]+:[0-9]+", hora)

                if hora_extraida is None:
                    continue

                hora = hora_extraida.group(0)

                horario = Horario(linha.codigo, sentido, hora, dia)
                horarios.append(horario)

    return horarios
