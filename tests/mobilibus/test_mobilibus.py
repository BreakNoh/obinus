from obinus.core.tipos import Json
from obinus.scrapers.mobilibus import QUERY_HORARIOS, QUERY_LINHAS, InterfaceMobilibus
from utils import *
from pathlib import Path
import json

am_lin, am_hor, am_hor_alt = carregar(
    Path(__file__).parent,
    ["amostra_linhas.json", "amostra_horarios.json", "amostra_horarios_alt.json"],
)

raspador = InterfaceMobilibus()
raspador.ID_PROJETO = "0"


def test_extrair_linhas():
    amostra = Json(QUERY_LINHAS.search(json.loads(am_lin)))
    linhas = raspador.extrair_linhas(amostra)

    assert len(linhas) == 3


def test_extrair_horarios():
    amostra = Json(QUERY_HORARIOS.search(json.loads(am_hor)))
    servicos = raspador.extrair_horarios(amostra)

    assert len(servicos) == 3

    [checar_horario(s.horarios) for s in servicos]


def test_extrair_horarios_alt():
    amostra = Json(QUERY_HORARIOS.search(json.loads(am_hor_alt)))
    servicos = raspador.extrair_horarios(amostra)

    assert len(servicos) == 3
    [checar_horario(s.horarios) for s in servicos]
