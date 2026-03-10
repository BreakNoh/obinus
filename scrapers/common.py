import re
from bs4 import Tag
from dataclasses import dataclass, asdict
import csv


def salvar_csv(dados: list, nome_arquivo: str):
    if not dados:
        print(f"Aviso: A lista para {nome_arquivo} está vazia. Nada foi salvo.")
        return

    cabecalho = asdict(dados[0]).keys()

    try:
        with open(nome_arquivo, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=cabecalho, delimiter=";")

            writer.writeheader()
            for item in dados:
                writer.writerow(asdict(item))

        print(f"Sucesso! {len(dados)} registros salvos em: {nome_arquivo}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo {nome_arquivo}: {e}")


def normalizar(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def extrair_texto(tag: Tag):
    if not tag:
        return ""
    return normalizar("".join(tag.find_all(string=True, recursive=False)))


@dataclass
class Linha:
    codigo: str
    nome: str
    detalhe: str
    executivo: bool


@dataclass
class Horario:
    linha: str
    sentido: str
    hora: str
    dia: str
