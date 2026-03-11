import sqlite3
import os

ARQUIVO_DB = "../dados.db"
ARQUIVO_SCHEMA = "tabelas/schema.sql"
ARQUIVO_SEED = "tabelas/seed.sql"


def popular_db(cursor, conn):
    if os.path.exists(ARQUIVO_SEED):
        with open(ARQUIVO_SEED, "r", encoding="utf-8") as f:
            sql_script = f.read()

        cursor.executescript(sql_script)
        conn.commit()

        print("! tabelas semedas")
    else:
        print(f"X arquivo {ARQUIVO_SEED} não encontrado")


def iniciar_db():
    deve_popular = not os.path.exists(ARQUIVO_DB)
    conn = sqlite3.connect(ARQUIVO_DB)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA foreign_keys = ON;")

        if os.path.exists(ARQUIVO_SCHEMA):
            with open(ARQUIVO_SCHEMA, "r", encoding="utf-8") as f:
                sql_script = f.read()

            cursor.executescript(sql_script)
            conn.commit()

            if deve_popular:
                popular_db(cursor, conn)

            print("! tabelas criadas/verificadas com sucesso")
        else:
            print(f"X arquivo {ARQUIVO_SCHEMA} não encontrado")

    except sqlite3.Error as e:
        print(f"X erro ao configurar o banco: {e}")

    finally:
        conn.close()


iniciar_db()
