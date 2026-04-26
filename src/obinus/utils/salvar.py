from dataclasses import asdict
import json
from pathlib import Path
import re
from obinus.utils.texto import REMOCOES, encurtar, criar_slug, padronizar_texto
from obinus.core.tipos import *
import json


ARQUIVO_ATUAL = Path(__file__).resolve()
DIR_RAIZ = ARQUIVO_ATUAL.parents[3]
PASTA_OUTPUT = DIR_RAIZ / "output"
PASTA_OUTPUT.mkdir(parents=True, exist_ok=True)

TAMANHO_SEGURO = 20
TAMANHO_MAXIMO_SLUG = 30


def encurtar_nome(obj: Linha | Servico):
    PADRAO_LINHA = re.compile(
        r"\(?P<via>(via\W.*?)[^\w\ ]+$|(?P<lixo>\(.*\))", re.IGNORECASE
    )

    if isinstance(obj, Linha):
        if len(obj.nome) < TAMANHO_SEGURO:
            return

        for i in PADRAO_LINHA.finditer(obj.nome):
            obj.nome = obj.nome.replace(i.group(), "")

            for i in i.groupdict():
                if i[0] == "lixo":
                    continue

                if obj.detalhe:
                    obj.detalhe += f"\n{i[1]}"
                else:
                    obj.detalhe = str(i[1])

        obj.nome = encurtar(obj.nome, lista_negra=set(), truncar=False) or ""

    else:
        if not obj.sentido or len(obj.sentido) < TAMANHO_SEGURO:
            return

        obj.sentido = encurtar(obj.sentido, truncar=False, lista_negra=set())


def identificar(obj: Empresa | Linha):
    if isinstance(obj, Empresa):
        obj.slug = criar_slug(obj.nome)

    elif isinstance(obj, Linha):
        encurtar_nome(obj)  # encurta o nome após usar para gerar hash
        nome_slug = (
            encurtar(obj.nome, truncar=len(obj.nome or "") > TAMANHO_SEGURO) or ""
        )

        slug = criar_slug(f"{obj.codigo or ''} {nome_slug}")
        obj.slug = slug


def normalizar(obj: Linha | Servico | Horario | ObsHorario):
    if isinstance(obj, Linha):
        obj.nome = padronizar_texto(obj.nome) or ""
        obj.detalhe = padronizar_texto(obj.detalhe)

        for s in obj.servicos:
            normalizar(s)

    elif isinstance(obj, Servico):
        obj.sentido = padronizar_texto(obj.sentido)

        for h in obj.horarios:
            normalizar(h)
    elif isinstance(obj, Horario):
        PADRAO_HORA = re.compile(r"(?P<h>\d{1,2})\D*(?P<m>\d{1,2})")

        if match := PADRAO_HORA.search(obj.hora):
            hrs = match.group("h")
            min = match.group("m")
            obj.hora = f"{hrs:0>2}:{min:0>2}"

        for o in obj.obs:
            normalizar(o)
    else:
        obj.valor = padronizar_texto(obj.valor) or obj.valor


def salvar_json(dados: dict | list, arquivo: str | Path):
    if not dados:
        return

    try:
        caminho = PASTA_OUTPUT / arquivo
        caminho.parent.mkdir(parents=True, exist_ok=True)

        with open(caminho, "w", encoding="utf-8") as arq:
            dados_serializados = json.dumps(dados, ensure_ascii=False, indent=4)
            arq.write(dados_serializados)

    except Exception as e:
        print(e)
    pass
