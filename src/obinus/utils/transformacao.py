from dataclasses import replace
from obinus.core.tipos import Empresa, Linha
import re
from unidecode import unidecode


def _normalizar_texto(texto: str) -> str:
    resultado = texto.strip()
    resultado = re.sub(r"\s+", " ", resultado)  # normaliza espaços
    resultado = re.sub(r"^\W+|\W+$", "", resultado)  # retira simbolos das extremidades
    resultado = resultado.title()  # Capitaliza Corretamente
    return resultado


def normalizar_nome(empresa: Empresa) -> Empresa:
    return replace(
        empresa,
        nome=_normalizar_texto(empresa.nome),
        linhas=[
            replace(
                L,
                nome=_normalizar_texto(L.nome),
                servicos=[
                    replace(
                        S,
                        sentido=_normalizar_texto(S.sentido) if S.sentido else None,
                    )
                    for S in L.servicos
                ],
            )
            for L in empresa.linhas
        ],
    )


def _criar_slug(texto: str, tamanho_max: int = 30) -> str:
    slug = unidecode(texto.lower().strip())  # deixa minuscula e remove acentos
    slug = _encurtar_nome(slug, agressivo=True)
    slug = re.sub(r"\W+", "-", slug)  # troca tudo que não for letra/numero por -

    tamanho = min(len(slug), tamanho_max)
    slug_limpa = re.sub(r"\W$", "", slug[:tamanho])

    return slug_limpa


def adicionar_slug(empresa: Empresa) -> Empresa:
    return replace(
        empresa,
        slug=_criar_slug(empresa.nome),
        linhas=[
            replace(
                L,
                slug=_criar_slug(f"{L.codigo} {L.nome}" if L.codigo else L.nome),
            )
            for L in empresa.linhas
        ],
    )


def _extrair_detalhe(linha: Linha) -> Linha:
    if match := re.search(
        r"(?P<nom>^.+?)(?P<det>\bvia\b.+$)", linha.nome, re.IGNORECASE
    ):
        nome = match.group("nom").strip()
        detalhe = match.group("det").strip()

        return replace(
            linha,
            nome=nome,
            detalhe=f"{detalhe}\n{linha.detalhe}" if linha.detalhe else detalhe,
        )

    return linha


def extrair_detalhe_nome(empresa: Empresa) -> Empresa:
    return replace(
        empresa,
        linhas=[_extrair_detalhe(L) for L in empresa.linhas],
    )


def _encurtar_nome(nome: str, agressivo: bool = False) -> str:
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

    ABREVIACAO_LEVE = {
        "plataforma": "plat",
        "rua": "r",
        "avenida": "av",
        "estacao": "est",
        "loteamento": "lot",
        "hospital": "hosp",
        "governador": "gov",
        "rodovia": "rod",
        "expresso": "exp",
    }

    ABREVIACAO_PESADA = {
        "linha": "lin",
        "florianopolis": "fpolis",
        "santo": "sto",
        "santa": "sta",
        "industria": "ind",
        "industrial": "ind",
        "fazenda": "faz",
        "circular": "circ",
        "terminal": "term",
        "volta": "vlt",
        "partida": "ptd",
        "partidas": "ptd",
        "saida": "sai",
        "saidas": "sai",
        "coletivo": "col",
        "transporte": "trans",
    }

    resultado = nome

    if agressivo:
        for i in [*REMOCOES, *PREPOSICOES]:
            resultado = re.sub(rf"\b{i}\b", "", resultado, re.IGNORECASE)

        for k, v in {**ABREVIACAO_PESADA, **ABREVIACAO_LEVE}.items():
            resultado = re.sub(rf"\b{k}\b", v, resultado, re.IGNORECASE)
    else:
        for k, v in ABREVIACAO_LEVE.items():
            resultado = re.sub(rf"\b{k}\b", v, resultado, re.IGNORECASE)

    return re.sub(r"\s+", " ", resultado).strip()


def encurtar_nome(empresa: Empresa) -> Empresa:
    return replace(
        empresa,
        linhas=[
            replace(
                _extrair_detalhe(L),
                servicos=[
                    replace(S, sentido=_encurtar_nome(S.sentido) if S.sentido else None)
                    for S in L.servicos
                ],
            )
            for L in empresa.linhas
        ],
    )
