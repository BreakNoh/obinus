from dataclasses import asdict
from pathlib import Path
import csv


ARQUIVO_ATUAL = Path(__file__).resolve()
DIR_ATUAL = ARQUIVO_ATUAL.parent
DIR_PACOTE = DIR_ATUAL.parent
DIR_RAIZ = DIR_PACOTE.parent.parent
PASTA_SQL = DIR_ATUAL / "sql"
PASTA_OUTPUT = DIR_RAIZ / "output"

PASTA_OUTPUT.mkdir(parents=True, exist_ok=True)


def salvar_csv(dados: list, nome_arquivo: str):
    if not dados:
        return

    cabecalho = asdict(dados[0]).keys()

    try:
        caminho = PASTA_OUTPUT / nome_arquivo
        caminho.parent.mkdir(parents=True, exist_ok=True)

        with open(caminho, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=cabecalho, delimiter=";")

            writer.writeheader()
            for item in dados:
                writer.writerow(asdict(item))

        print(f"> {len(dados)} registros salvos em: {nome_arquivo}")
    except Exception as e:
        print(f"X erro ao salvar csv: ", e)
