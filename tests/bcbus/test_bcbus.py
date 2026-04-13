from bs4 import BeautifulSoup
from obinus.core.tipos import Html
import utils
from obinus.scrapers.vale_do_itajai.bcbus import BCBus

ams_lin, ams_hor = utils.carregar(
    utils.Path(__file__).parent, ["amostra_linhas.html", "amostra_horarios.html"]
)

raspador = BCBus()


def test_extrair_linhas():
    html = BeautifulSoup(ams_lin, "html.parser")
    linhas = raspador.extrair_linhas(Html(html))

    assert len(linhas) == 2


def test_extrair_horarios():
    html = BeautifulSoup(ams_hor, "html.parser")
    servicos = raspador.extrair_horarios(Html(html))

    assert len(servicos) == 4
    assert len(servicos[0].horarios) == 2
    assert len(servicos[1].horarios) == 1

    [utils.checar_horario(s.horarios) for s in servicos]
