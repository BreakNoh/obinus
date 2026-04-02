from utils import *
from obinus.scrapers.grande_floripa.tcestrela import TCEstrela
from obinus.core.tipos import *
from pathlib import Path

amos_linha, amos_horas = carregar_amostras(Path(__file__).parent)
raspador = TCEstrela()


def test_extrair_linhas():
    assert len(raspador.extrair_linhas(amos_linha)) == 3


def test_extrair_legeda():
    assert len(raspador.extrair_legenda(amos_horas.html)) == 2


def test_extrair_horarios():
    assert len(raspador.extrair_horarios(amos_horas)) == 2
