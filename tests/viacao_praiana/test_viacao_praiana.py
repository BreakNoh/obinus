import utils
from obinus.scrapers.vale_do_itajai.viacao_praiana import ViacaoPraiana

ams_lin, ams_hor = utils.carregar(
    utils.Path(__file__).parent, ["amostra_linhas.html", "amostra_horarios.html"]
)

raspador = ViacaoPraiana()


def test_extrair_linhas():
    html = utils.BeautifulSoup(ams_lin, "html.parser")
    linhas = raspador.extrair_linhas(utils.Html(html))

    assert len(linhas) == 3


def test_extrair_horarios():
    html = utils.BeautifulSoup(ams_hor, "html.parser")
    servicos = raspador.extrair_horarios(utils.Html(html))

    assert len(servicos) == 4
    assert len(servicos[0].horarios) == 1
    assert len(servicos[1].horarios) == 2
    assert len(servicos[2].horarios) == 3

    assert len(servicos[3].horarios) == 23
    assert servicos[3].sentido == "Camboriú - Itajaí via SANTA REGINA - AREIAS"
    assert servicos[3].dias == utils.DIAS_UTEIS
