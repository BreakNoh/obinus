from obinus.core.base import Raspador
from obinus.scrapers.norte.coletivo_rainha import ColetivoRainha
from obinus.scrapers.norte.gidion_transtusa import GidionTranstusa
from .scrapers.grande_florianopolis import *
from .core.modelos import *
from .database import db
from .utils.salvar import salvar_csv
from .scrapers.mobilibus import Mobilibus

todas_linhas: list[Linha] = []
todos_horarios: list[Horario] = []

scrapers = [Biguacu(), Fenix(), Estrela(), SantaTerezinha(), Imperatriz(), Jotur()]


def main():
    db.iniciar_db()

    for raspador in scrapers:
        linhas, horarios = raspador.raspar()

        todas_linhas.extend(linhas)
        todos_horarios.extend(horarios)

        salvar_csv(linhas, f"LINHAS_{raspador.empresa()}.csv")
        salvar_csv(horarios, f"HORARIOS_{raspador.empresa()}.csv")

    print("# salvando linhas...")
    db.salvar_linhas(todas_linhas)

    print("# salvando horarios...")
    db.salvar_horarios(todos_horarios)


def empresas():
    global scrapers
    import sys

    selecionados = []

    for e in sys.argv:
        for s in scrapers:
            if s.empresa().lower() == e.lower():
                selecionados.append(s)

    scrapers = selecionados
    main()


def testar_mobilibus():
    raspador = Mobilibus(332, lambda s: s)
    # print(raspador.raspar())
    raspador.raspar()


def testar_gidion():
    raspador = ColetivoRainha()
    raspador.raspar()


def teste():
    global scrapers
    from .scrapers.teste import Teste

    scrapers = [Teste()]

    main()
