from dataclasses import asdict
import sqlite3
import os

from common import Horario, Linha
from config import PATHS
from db import queries

SCHEMA = PATHS["schema"]
SEED = PATHS["seed"]
ARQUIVO = PATHS["db"]

conexao = sqlite3.connect(ARQUIVO)
cursor = conexao.cursor()

cursor.execute("PRAGMA foreign_keys = ON;")


def iniciar_db():
    if not os.path.exists(SCHEMA):
        print("schema não encontrado")
        return

    with open(SCHEMA, "r") as f:
        script = f.read()

        try:
            cursor.executescript(script)
            conexao.commit()
        except Exception as e:
            conexao.rollback()
            print("erro ao iniciar db", e)


def popular_db():
    if not os.path.exists(SEED):
        return

    with open(SEED, "r") as f:
        script = f.read()

        try:
            cursor.executescript(script)
            conexao.commit()
        except Exception as e:
            conexao.rollback()
            print("erro ao popular db", e)


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
