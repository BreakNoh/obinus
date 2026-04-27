import re
import random
from bs4 import Tag
from obinus.core.tipos import DIAS_UTEIS, DOMINGO_E_FERIADOS, SABADO, Dias
from unidecode import unidecode


def normalizar(s: str) -> str:
    s = str(s)
    return re.sub(r"\s+", " ", s).strip()


def extrair_texto(tag: Tag | None):
    if not tag or tag is None:
        return ""
    return normalizar("".join(tag.find_all(string=True, recursive=False)))


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


PREPOSICOES = {
    "dos",
    "das",
    "do",
    "da",
    "de",
    "para",
    "pra",
    "ate",
}

REMOCOES = {
    "os",
    "as",
    "o",
    "a",
    "e",
    "via",
}

ABREVIACOES = {
    "plataforma": "plat",
    "loteamento": "lot",
    "estacao": "est",
    "avenida": "av",
    "rua": "r",
    "linha": "lin",
    "governador": "gov",
    "florianopolis": "fpolis",
    "hospital": "hosp",
    "santo": "sto",
    "santa": "sta",
    "industria": "ind",
    "industrial": "ind",
    "fazenda": "faz",
    "circular": "circ",
    "terminal": "term",
    "rodovia": "rod",
    "expresso": "expr",
    "volta": "vlt",
    "partida": "ptd",
    "partidas": "ptd",
    "saida": "sai",
    "saidas": "sai",
    "coletivo": "col",
}


def truncar_palavras(
    tokens: list[str],
    tamanho_alvo: int = 4,
    final_consoante: bool = True,
    lista_branca: set[str] = set(ABREVIACOES.values()),
) -> list[str]:
    tokens_truncados = []

    for tkn in tokens:
        if len(tkn) < tamanho_alvo or tkn in lista_branca:
            tokens_truncados.append(tkn)
            continue

        tam = tamanho_alvo
        if final_consoante:
            vogais = "aeiouáéíóúâêôãõ"

            while (
                tam < tamanho_alvo + 2
                and tam < len(tkn)
                and tkn[tam - 1].lower() in vogais
            ):
                tam += 1

        tokens_truncados.append(tkn[:tam])

    return tokens_truncados


def remover_palavras(
    tokens: list[str],
    lista_negra: set[str] = REMOCOES | PREPOSICOES,
    lista_branca: set[str] = set(),
) -> list[str]:
    tokens_limpos = []

    for t in tokens:
        t_norm = unidecode(t).lower()
        if t_norm in lista_branca or t_norm not in lista_negra:
            tokens_limpos.append(t)

    return tokens_limpos


def abreviar_palavras(
    tokens: list[str], tabela: dict[str, str] = ABREVIACOES
) -> list[str]:
    return [tabela.get(unidecode(t), t) for t in tokens]


def padronizar_texto(texto: str | None) -> str | None:
    if not texto:
        return None

    texto_sem_rebarbas = re.sub(r"^[^\w\(\)]+|[^\w\(\)]+$", "", texto)
    texto_primeira_maiuscula = texto_sem_rebarbas.lower().title()

    return texto_primeira_maiuscula


def encurtar(
    s: str | None,
    alvo: int = 20,
    abreviacoes: dict[str, str] = ABREVIACOES,
    lista_branca: set[str] = set(ABREVIACOES.values()),
    lista_negra: set[str] = REMOCOES | PREPOSICOES,
    truncar=True,
) -> str | None:
    if s is None:
        return None

    tokens = re.split(r"\b", s)

    tokens = remover_palavras(
        tokens, lista_negra=lista_negra, lista_branca=lista_branca
    )
    if sum(len(t) for t in tokens) > alvo:
        tokens = abreviar_palavras(tokens, tabela=abreviacoes)

    if truncar and sum(len(t) for t in tokens) > alvo:
        tokens = truncar_palavras(tokens, lista_branca=lista_branca)

    encurtado = "".join(tokens)

    return re.sub(r"\s+", " ", encurtado)


TAMANHO_MAXIMO_SLUG = 30


def criar_slug(texto: str) -> str:
    PADRAO_REBARBA = re.compile(r"^\W+|\W+$")

    slug = unidecode(texto.lower().strip())  # deixa minuscula e remove acentos

    slug = PADRAO_REBARBA.sub("", slug)  # strip melhorado

    for i, j in [
        (r"\bexpresso\b", "exp"),
        (r"\bcoletivo\b", "col"),
        (r"\btransporte(s)?\b", "trans"),
    ]:
        slug = re.sub(i, j, slug)

    slug = re.sub(r"\W+", "-", slug)  # troca tudo que não for letra/numero por -

    tamanho = min(len(slug), TAMANHO_MAXIMO_SLUG)
    slug_limpa = PADRAO_REBARBA.sub("", slug[:tamanho])

    return slug_limpa
