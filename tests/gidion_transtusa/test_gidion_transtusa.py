from json import loads
from obinus.scrapers.norte.gidion_transtusa import (
    GidionTranstusa,
    QUERY_HORARIOS,
    QUERY_LINHAS,
)
from utils import *

am_lin, am_hor = carregar(
    Path(__file__).parent, ["amostra_linhas.json", "amostra_horarios.json"]
)
raspador = GidionTranstusa()


def test_extrair_lihas():
    json = QUERY_LINHAS.search(loads(am_lin))
    linhas = raspador.extrair_linhas(Json(json))

    assert len(linhas) == 3


def test_extrair_horarios():
    json = QUERY_HORARIOS.search(loads(am_hor))
    servicos = raspador.extrair_horarios(Json(json))

    assert len(servicos) == 2
    assert len(servicos[0].horarios) == 3
    assert servicos[0].dias == DIAS_UTEIS
    assert len(servicos[1].horarios) == 1
    assert servicos[1].dias == SABADO
