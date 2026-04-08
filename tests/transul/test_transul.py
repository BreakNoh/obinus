from bs4 import BeautifulSoup
from obinus.core.tipos import Html
import utils
from obinus.scrapers.serrana.transul import Transul

ams_lin, ams_hor = utils.carregar(
    __file__, ["amostra_linhas.html", "amostra_horarios.html"]
)
raspador = Transul()


def test_extrair_linhas():
    html = Html(BeautifulSoup(ams_lin, "html.parser"))
    linhas = raspador.extrair_linhas(html)

    assert len(linhas) == 5
    assert linhas[3][0].nome == "BELA VISTA"
    assert linhas[4][0].nome == "CIDADE ALTA via BR 282"
    assert linhas[3][1] == utils.Url("https://transullages.com.br/linha/41/bela-vista")
    assert linhas[4][1] == utils.Url(
        "https://transullages.com.br/linha/44/cidade-alta-via-br-282"
    )


def test_extrair_horarios():
    html = Html(BeautifulSoup(ams_hor, "html.parser"))
    servicos = raspador.extrair_horarios(html)

    assert len(servicos) == 5
    assert servicos[3].sentido == "Saída Terminal"
    assert servicos[4].sentido == "Saída Bairro"
