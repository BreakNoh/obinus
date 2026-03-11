import re
import random
from bs4 import Tag


def texto_aleatorio(tam: int, chars: str = "abcdefghijklmnopqrstuvwxyz") -> str:
    resultado = ""
    for _ in range(tam):
        resultado += random.choice(chars)

    return resultado


def normalizar(s: str) -> str:
    s = str(s)
    return re.sub(r"\s+", " ", s).strip()


def extrair_texto(tag: Tag | None):
    if not tag or tag is None:
        return ""
    return normalizar("".join(tag.find_all(string=True, recursive=False)))
