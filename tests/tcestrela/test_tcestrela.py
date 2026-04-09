from utils import *
from obinus.scrapers.grande_floripa.tcestrela import TCEstrela
from obinus.core.tipos import *
from pathlib import Path
from pprint import pprint

amos_linha, amos_horas = carregar_amostras(Path(__file__).parent)
raspador = TCEstrela()


def test_extrair_linhas():
    assert len(raspador.extrair_linhas(amos_linha)) == 3


def test_extrair_legeda():
    legendas = raspador.extrair_legenda(amos_horas.html)
    assert len(legendas) == 2
    assert legendas[0] == ("A", ItinerarioDiferenciado("via abc"))
    assert legendas[1] == ("*", HorarioPrevisto())


def test_extrair_horarios():
    servicos = raspador.extrair_horarios(amos_horas)
    assert len(servicos) == 6

    assert servicos[0].horarios[0].obs == [ItinerarioDiferenciado("via abc")]
    assert servicos[0].horarios[1].obs == [HorarioPrevisto()]
