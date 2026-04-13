from pathlib import Path
from utils import *
from obinus.scrapers.grande_floripa.jotur import Jotur

amostra_linhas, amostra_horarios = carregar_amostras(Path(__file__).parent)


def test_extrair_linhas():
    linhas = Jotur().extrair_linhas(amostra_linhas)
    assert len(linhas) == 3

    assert linhas[0][0].nome == "Linha A"
    assert linhas[0][0].detalhe == "Via Teste 123"


def test_extrair_horarios():
    servicos = Jotur().extrair_horarios(amostra_horarios)
    assert len(servicos) == 2
    assert servicos[0].dias == DIAS_UTEIS
    assert servicos[1].dias == SABADO
    assert servicos[0].horarios[0].hora == "11:11"
    [checar_horario(s.horarios) for s in servicos]
