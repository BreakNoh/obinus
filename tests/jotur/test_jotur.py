from pathlib import Path
from obinus.core.tipos import DIAS_UTEIS, SABADO
from utils import carregar_amostras
from obinus.scrapers.grande_floripa.jotur import Jotur

amostra_linhas, amostra_horarios = carregar_amostras(Path(__file__).parent)


def test_extrair_linhas():
    assert len(Jotur().extrair_linhas(amostra_linhas)) == 3


def test_extrair_horarios():
    servicos = Jotur().extrair_horarios(amostra_horarios)
    assert len(servicos) == 2
    assert servicos[0].dias == DIAS_UTEIS
    assert servicos[1].dias == SABADO
    assert servicos[0].horarios[0].hora == "11:11"
