from .core.modelos import *
from .database import db
from .utils.salvar import salvar_csv
from .scrapers import todos

todas_linhas: list[Linha] = []
todos_horarios: list[Horario] = []


def main():
    todas_linhas = []
    todos_horarios = []

    for raspador in todos:
        linhas, horarios = raspador.raspar()

        todas_linhas.extend(linhas)
        todos_horarios.extend(horarios)

        salvar_csv(linhas, f"LINHAS_{raspador.empresa()}.csv")
        salvar_csv(horarios, f"HORARIOS_{raspador.empresa()}.csv")

    salvar_csv(todas_linhas, "LINHAS_SANTA_CATARINA.csv")
    salvar_csv(todos_horarios, "HORARIOS_SANTA_CATARINA.csv")
