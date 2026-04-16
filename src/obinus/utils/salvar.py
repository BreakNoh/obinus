from dataclasses import asdict
import json
from pathlib import Path
import csv
import hashlib
import re
from unidecode import unidecode
from obinus.core.tipos import *


ARQUIVO_ATUAL = Path(__file__).resolve()
DIR_ATUAL = ARQUIVO_ATUAL.parent
DIR_PACOTE = DIR_ATUAL.parent
DIR_RAIZ = DIR_PACOTE.parent.parent
PASTA_SQL = DIR_ATUAL / "sql"
PASTA_OUTPUT = DIR_RAIZ / "output"

PASTA_OUTPUT.mkdir(parents=True, exist_ok=True)

ABREVIACOES = {
    "plataforma": "plat",
    "loteamento": "lot",
    "avenida": "av",
    "rua": "r",
    "governador": "gov",
    "florianopolis": "fpolis",
    "florianópolis": "fpolis",
}


def abreviar(s: str) -> str:
    resultado = s

    return s


def padronizar_texto(texto: str | None) -> str | None:
    if not texto:
        return None
    texto_sem_rebarbas = re.sub(r"^[^\w\(\)]+|[^\w\(\)]+$", "", texto)
    texto_primeira_maiuscula = texto_sem_rebarbas.lower().title()

    return texto_primeira_maiuscula


def criar_slug(texto: str) -> str:
    slug = unidecode(texto.lower().strip())  # deixa minuscula e remove acentos
    slug = re.sub(r"^\W+|\W+$", "", slug)  # strip melhorado
    slug = re.sub(r"\W+", "-", slug)  # troca tudo que não for letra/numero por -

    return slug


def encurtar_nome(obj: Linha | Servico):
    TAMANHO_SEGURO = 15
    PADRAO_LINHA = re.compile(
        r"\(?P<via>(via\W.*?)[^\w\ ]+$|(?P<lixo>\(.*\))", re.IGNORECASE
    )
    PADRAO_SERVICO = re.compile(
        r"\(.*\)|(via|sa[i\í]da(s)?|partida(s)?|sentido)\W*", re.IGNORECASE
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

    else:
        if not obj.sentido or len(obj.sentido) < TAMANHO_SEGURO:
            return

        obj.sentido = PADRAO_SERVICO.sub("", obj.sentido).strip()


def identificar(obj: Empresa | Linha | Servico | Horario, prefixo: str):
    if isinstance(obj, Empresa):
        obj.slug = criar_slug(obj.nome)

        for l in obj.linhas:
            identificar(l, obj.id)
    elif isinstance(obj, Linha):
        obj.id = gerar_id(obj.codigo or obj.nome, prefixo)

        encurtar_nome(obj)  # encurta o nome após usar para gerar hash
        obj.slug = criar_slug(f"{obj.codigo or ''} {obj.nome or ''}")

        for s in obj.servicos:
            identificar(s, obj.id)
    elif isinstance(obj, Servico):
        obj.id = gerar_id(obj.sentido or "", prefixo)

        encurtar_nome(obj)
        obj.slug = criar_slug(obj.sentido or "")

        for h in obj.horarios:
            identificar(h, obj.id)
    else:  # horario
        obs_ser = json.dumps(
            obj.obs,
            sort_keys=True,
            ensure_ascii=False,
            default=lambda o: o.__dict__,
        )

        obj.id = gerar_id(obj.hora + obs_ser, prefixo, tamanho=12)


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


def gerar_rows(empresa: Empresa) -> dict[str, list]:
    rows = {"horarios": [], "servicos": [], "linhas": [], "empresas": []}

    rows["empresas"].append(
        {
            "id": empresa.id,
            "nome": empresa.nome,
            "regioes": empresa.regioes,
            "slug": empresa.slug,
            "fonte": empresa.fonte,
        }
    )
    for linha in empresa.linhas:
        rows["linhas"].append(
            {
                "id": linha.id,
                "id_empresa": empresa.id,
                "nome": linha.nome,
                "codigo": linha.codigo,
                "detalhe": linha.detalhe,
                "slug": linha.slug,
            }
        )

        for servico in linha.servicos:
            servico_ser = {
                "id": servico.id,
                "id_linha": linha.id,
                "sentido": servico.sentido,
                "dias": servico.dias,
                "slug": servico.slug,
            }
            if not servico_ser in rows["servicos"]:
                rows["servicos"].append(servico_ser)

            for horario in servico.horarios:
                # obs_ser = f"[{','.join([str(obs) for obs in horario.obs] or [])}]"

                rows["horarios"].append(
                    {
                        "id": horario.id,
                        "id_servico": servico.id,
                        "hora": horario.hora,
                        "observacoes": json.dumps(
                            horario.obs,
                            sort_keys=True,
                            ensure_ascii=False,
                            default=lambda o: o.__dict__,
                        ),
                    }
                )

    return rows


def gerar_id(identificador: str, prefixo: str, tamanho: int = 8) -> str:
    _identificador = identificador.lower().strip()
    _prefixo = prefixo.lower().strip()

    segredo = f"{_prefixo}:{_identificador}"
    hash = hashlib.sha256(segredo.encode()).hexdigest()

    return hash[:tamanho]


def salvar_csv(dados: list, nome_arquivo: str):
    if not dados:
        return

    try:
        cabecalho = asdict(dados[0]).keys()
    except:
        if isinstance(dados[0], dict):
            cabecalho = dados[0].keys()
        else:
            print("erro ao salvar csv")
            return

    try:
        caminho = PASTA_OUTPUT / nome_arquivo
        caminho.parent.mkdir(parents=True, exist_ok=True)

        with open(caminho, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=cabecalho, delimiter=";")

            writer.writeheader()
            for item in dados:
                try:
                    writer.writerow(asdict(item))
                except:
                    if isinstance(item, dict):
                        writer.writerow(item)

        print(f"> {len(dados)} registros salvos em: {nome_arquivo}")
    except Exception as e:
        print(f"X erro ao salvar csv: ", e)
