from utils import *
from obinus.scrapers.grande_floripa.tcimperatriz import TCImperatriz

from pathlib import Path

[amostra_linhas, amostra_horarios] = carregar_amostras(Path(__file__).parent)


def test_extrair_linhas():
    assert len(TCImperatriz().extrair_linhas(amostra_linhas)) == 3


def test_extrair_horarios():
    servicos = TCImperatriz().extrair_horarios(amostra_horarios)
    assert len(servicos) == 2
    assert len(servicos[0].horarios) == 3
    assert len(servicos[1].horarios) == 1

    [checar_horario(s.horarios) for s in servicos]
