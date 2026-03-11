from common import Horario, Linha, salvar_csv
import grande_floripa

todas_linhas: list[Linha] = []
todos_horarios: list[Horario] = []

for raspador in grande_floripa.todos:
    print(f"! raspando {raspador.empresa()}")
    linhas: list[Linha] = raspador.raspar_linhas()

    print(f"! {raspador.empresa()}: {len(linhas)} linhas raspadas")

    horarios: list[Horario] = []

    for linha in linhas:
        print(f"> raspando {linha.codigo} - {linha.nome}...")
        horarios_ = raspador.raspar_horarios_linha(linha)
        horarios.extend(horarios_)

    print(f"! {raspador.empresa()}: {len(horarios)} horarios raspados")

    todas_linhas.extend(linhas)
    todos_horarios.extend(horarios)

print("! salvando dados...")

salvar_csv(todas_linhas, "out/linhas.csv")
salvar_csv(todos_horarios, "out/horarios.csv")

print("! dados salvos")

print("! operacao concluida")
