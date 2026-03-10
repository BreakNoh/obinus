import requests
import sys
from bs4 import BeautifulSoup
from common import *

URL_BASE = "https://www.tcbiguacu.com.br"
URL_BUSCA_LINHAS = URL_BASE + "/sistema/sys/AJAX_search_line.php"
URL_HORARIOS = URL_BASE + "/sistema/sys/AJAX_get_line_hours.php"


def raspar_linhas(dom: BeautifulSoup, executivo: bool) -> list[Linha]:
    linhas = []
    for li in dom.find_all("li"):
        codigo, nome, detalhe = "", "", ""

        if tag_c := li.find(class_="code-line"):
            codigo = extrair_texto(tag_c)

        if tag_n := li.find(class_="name-line"):
            nome = extrair_texto(tag_n)

        if tag_d := li.find("span"):
            detalhe = extrair_texto(tag_d)

        linhas.append(Linha(codigo, nome, detalhe, executivo))

    return linhas


def raspar_horarios(dom: BeautifulSoup, linha: str, dia: str) -> list[Horario]:
    horarios = []

    for s in dom.find_all(class_="hours-line"):
        sentido = ""

        if tag_s := s.find(class_="title"):
            sentido = extrair_texto(tag_s)

        for h in s.find_all(class_="hour"):
            hora = extrair_texto(h)

            horarios.append(Horario(linha, sentido, hora, dia))

    return horarios


print("Raspando linhas...")

sessao = requests.Session()

html_conv = sessao.get(URL_BUSCA_LINHAS, params={"busca": "", "id_grupo_bus": 0})
html_exec = sessao.get(URL_BUSCA_LINHAS, params={"busca": "", "id_grupo_bus": 5})

dom_conv = BeautifulSoup(html_conv.text, "html.parser")
dom_exec = BeautifulSoup(html_exec.text, "html.parser")

linhas: list[Linha] = []
linhas.extend(raspar_linhas(dom_conv, False))
linhas.extend(raspar_linhas(dom_exec, True))


salvar_csv(linhas, "out/linhas_biguacu.csv")

if "--linhas" in sys.argv:
    sys.exit(0)

horarios = []

DIAS = {1: "UTIL", 2: "SABADO", 3: "DOMINGO_FERIADO"}

for l in linhas:
    print(f"Raspando horários da linha {l.codigo} - {l.nome}...")
    codigo = l.codigo

    for id_dia, dia in DIAS.items():
        html = sessao.get(
            URL_HORARIOS, params={"id_line_bus": codigo, "id_day_week": id_dia}
        ).text

        horarios.extend(
            raspar_horarios(BeautifulSoup(html, "html.parser"), codigo, dia)
        )

salvar_csv(horarios, "out/horarios_biguacu.csv")
