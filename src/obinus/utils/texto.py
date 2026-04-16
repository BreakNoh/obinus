import re
import random
from bs4 import Tag

from obinus.core.tipos import DIAS_UTEIS, DOMINGO_E_FERIADOS, SABADO, Dias


def texto_aleatorio(tam: int, chars: str = "abcdefghijklmnopqrstuvwxyz") -> str:
    resultado = ""
    for _ in range(tam):
        resultado += random.choice(chars)

    return resultado


def normalizar_dia(s: str) -> Dias:
    normalizado = (
        s.lower().strip().replace("á", "a").replace("ú", "u").replace("à", "a")
    )
    testes = {
        "letivo": DIAS_UTEIS,
        "du": DIAS_UTEIS,
        "dia ": DIAS_UTEIS,
        "dias": DIAS_UTEIS,
        "util": DIAS_UTEIS,
        "uteis": DIAS_UTEIS,
        "seg": DIAS_UTEIS,
        "sex": DIAS_UTEIS,
        "dom": DOMINGO_E_FERIADOS,
        "feri": DOMINGO_E_FERIADOS,
        "sab": SABADO,
        "todos": DIAS_UTEIS | SABADO | DOMINGO_E_FERIADOS,
        "diari": DIAS_UTEIS | SABADO | DOMINGO_E_FERIADOS,
    }
    dias = 0
    for teste, dia in testes.items():
        if teste in normalizado:
            dias |= dia

    return dias


def normalizar(s: str) -> str:
    s = str(s)
    return re.sub(r"\s+", " ", s).strip()


def extrair_texto(tag: Tag | None):
    if not tag or tag is None:
        return ""
    return normalizar("".join(tag.find_all(string=True, recursive=False)))
