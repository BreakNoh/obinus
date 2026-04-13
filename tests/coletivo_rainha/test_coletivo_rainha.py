from json import loads
from utils import *
from obinus.scrapers.norte.coletivo_rainha import ColetivoRainha, QUERY_HORARIOS


raspador = ColetivoRainha()
am_lin, am_hor = carregar(
    Path(__file__).parent, ["amostra_linhas.html", "amostra_horarios.json"]
)


def test_extrair_linhas():
    html = BeautifulSoup(am_lin, "html.parser")
    linhas = raspador.extrair_linhas(Html(html))

    assert len(linhas) == 3


def test_extrair_horarios():
    json = QUERY_HORARIOS.search(loads(am_hor))

    servicos = raspador.extrair_horarios(Json(json))

    assert len(servicos) == 2
    [checar_horario(s.horarios) for s in servicos]
