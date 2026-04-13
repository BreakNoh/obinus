from pathlib import Path
import re
from bs4 import BeautifulSoup
from obinus.core.tipos import *
import json


def checar_horario(horarios: list[Horario]):
    PADRAO_HORARIO = re.compile(r"\d{2}:\d{2}")

    for h in horarios:
        assert PADRAO_HORARIO.search(h.hora) is not None


def carregar_amostras(raiz: Path) -> list[Html]:
    amostras = []

    for suf in ["linhas", "horarios"]:
        with open(raiz / f"amostra_{suf}.html", "r") as a:
            amostras.append(Html(BeautifulSoup(a.read(), "html.parser")))

    return amostras


def carregar(raiz: Path | str, arqs: list[str]) -> list[str]:
    if isinstance(raiz, str):
        _raiz = Path(raiz).parent
    else:
        _raiz = raiz

    amostras = []

    for arq in arqs:
        with open(_raiz / arq, "r") as a:
            amostras.append(a.read())

    return amostras
