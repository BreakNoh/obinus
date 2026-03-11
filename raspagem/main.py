from common import Horario, Linha, salvar_csv
import db.db as db
import grande_floripa as gf

todas_linhas: list[Linha] = []
todos_horarios: list[Horario] = []

db.iniciar_db()

for raspador in gf.todos:
    print(f"# raspando {raspador.empresa()}...")
    linhas_raspadas: list[Linha] = raspador.raspar_linhas()
    print(f"> {len(linhas_raspadas)} linhas raspadas")

    num_horarios = 0
    todas_linhas.extend(linhas_raspadas)
    # todos_horarios_raspados = []

    for linha in linhas_raspadas:
        horarios_raspados = raspador.raspar_horarios_linha(linha)
        num_horarios += len(horarios_raspados)

        # todos_horarios_raspados.extend(horarios_raspados)
        todos_horarios.extend(horarios_raspados)

    print(f"> {num_horarios} horarios raspados")

print("# salvando linhas...")
db.salvar_linhas(todas_linhas)

print("# salvando horarios...")
db.salvar_horarios(todos_horarios)
