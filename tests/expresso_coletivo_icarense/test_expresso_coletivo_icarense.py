import utils
from obinus.scrapers.sul.expresso_coletivo_icarense import ExpressoColetivoIcarense

ams_lin, ams_hor = utils.carregar(
    __file__, ["amostra_linhas.html", "amostra_horarios.html"]
)
raspador = ExpressoColetivoIcarense()


def test_extrair_linhas():
    hmtl = utils.BeautifulSoup(ams_lin, "html.parser")
    linhas = raspador.extrair_linhas(utils.Html(hmtl))
    assert len(linhas) == 4
    assert linhas[3][0].nome == "B.VELHA X CRICIUMA"


def test_extrair_horarios():
    hmtl = utils.BeautifulSoup(ams_hor, "html.parser")
    servicos = raspador.extrair_horarios(utils.Html(hmtl))

    assert len(servicos) == 3
    assert len(servicos[0].horarios) == 2
    assert len(servicos[2].horarios) == 1
    assert servicos[2].horarios[0].hora == "17:25"
    assert servicos[2].horarios[0].obs == [
        utils.ItinerarioDiferenciado("Via PV-MARILI-B.VISTA")
    ]
