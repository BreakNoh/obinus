from dataclasses import asdict
from pathlib import Path
import sqlite3
import os

from obinus.core.base import *
import obinus.database.queries as queries

ARQUIVO_ATUAL = Path(__file__).resolve()
DIR_ATUAL = ARQUIVO_ATUAL.parent
DIR_PACOTE = DIR_ATUAL.parent
DIR_RAIZ = DIR_PACOTE.parent.parent
PASTA_SQL = DIR_ATUAL / "sql"
PASTA_OUTPUT = DIR_RAIZ / "output"

PASTA_OUTPUT.mkdir(parents=True, exist_ok=True)

conexao = sqlite3.connect(PASTA_OUTPUT / "dados.db")
cursor = conexao.cursor()

cursor.execute("PRAGMA foreign_keys = ON;")


ARQUIVO_SCHEMA = PASTA_SQL / "schema.sql"


def iniciar_db():
    if not os.path.exists(ARQUIVO_SCHEMA):
        print("schema não encontrado")
        return

    with open(ARQUIVO_SCHEMA, "r") as f:
        script = f.read()

        # print(script)

        try:
            cursor.executescript(script)
            conexao.commit()
            print("db iniciada")
        except Exception as e:
            conexao.rollback()
            print("erro ao iniciar db", e)


# def popular_db():
#     if not os.path.exists(SEED):
#         return
#
#     with open(SEED, "r") as f:
#         script = f.read()
#
#         try:
#             cursor.executescript(script)
#             conexao.commit()
#         except Exception as e:
#             conexao.rollback()
#             print("erro ao popular db", e)


def salvar_linhas(linhas: list[Linha]):
    try:
        cursor.execute("DELETE FROM linhas")

        dicts = [asdict(linha) for linha in linhas]

        cursor.executemany(queries.INSERIR_LINHA, dicts)

        conexao.commit()
    except Exception as e:
        conexao.rollback()
        print("erro ao salvar linhas", e)


def salvar_horarios(horarios: list[Horario]):
    try:
        cursor.execute("DELETE FROM horarios")

        dicts = [asdict(horario) for horario in horarios]

        cursor.executemany(queries.INSERIR_HORARIO, dicts)

        conexao.commit()
    except Exception as e:
        conexao.rollback()
        print("erro ao salvar horarios", e)
