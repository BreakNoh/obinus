from pathlib import Path

from bs4 import BeautifulSoup

from obinus.core.tipos import Html


def carregar_amostras(raiz: Path) -> list[Html]:
    amostras = []

    for suf in ["linhas", "horarios"]:
        with open(raiz / f"amostra_{suf}.html", "r") as a:
            amostras.append(Html(BeautifulSoup(a.read(), "html.parser")))

    return amostras
