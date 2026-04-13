import utils
from obinus.scrapers.sul.grupo_forquilinhas import GrupoForquilhinhas

ams_lin, ams_hor = utils.carregar(
    __file__, ["amostra_linhas.html", "amostra_horarios.html"]
)
raspador = GrupoForquilhinhas()


def test_extrair_linhas():
    html = utils.BeautifulSoup(ams_lin, "html.parser")
    linhas = raspador.extrair_linhas(utils.Html(html))

    assert len(linhas) == 3
    assert linhas[2][0].nome == "Santa Cruz / Centro"
    assert linhas[2][0].codigo == "101"
    assert linhas[2][0].detalhe == "Via Ouro Negro / Nova York"


def test_extrair_horarios():
    html = utils.BeautifulSoup(ams_hor, "html.parser")
    servicos = raspador.extrair_horarios(utils.Html(html))

    assert len(servicos) == 3

    assert servicos[1].sentido == "Centro"
    assert len(servicos[1].horarios) == 1
    assert servicos[1].horarios[0] == utils.Horario(
        "06:55", [utils.ItinerarioDiferenciado("A")]
    )

    assert servicos[2].sentido == "Santa Cruz"
    assert len(servicos[2].horarios) == 2
    assert servicos[2].horarios[0] == utils.Horario("06:12")
    assert servicos[2].horarios[1] == utils.Horario(
        "06:12", [utils.ItinerarioDiferenciado("B")]
    )
    [utils.checar_horario(s.horarios) for s in servicos]
