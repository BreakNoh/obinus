import utils
from obinus.scrapers.sul.expresso_coletivo_icarense import ExpressoColetivoIcarense

ams_lin, ams_hor = utils.carregar(
    __file__, ["amostra_linhas.html", "amostra_horarios.html"]
)
raspador = ExpressoColetivoIcarense()


def test_extrair_linhas():
    hmtl = utils.BeautifulSoup(ams_lin, "html.parser")
    linhas = raspador.extrair_linhas(utils.Html(hmtl))

    assert len(linhas) == 3
