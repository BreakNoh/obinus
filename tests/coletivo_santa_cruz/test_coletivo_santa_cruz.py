from utils import *
from obinus.scrapers.norte.santa_cruz import SantaCruz, QUERY_LINHAS

am_hora_raw, am_hora = carregar(
    Path(__file__).parent, ["amostra_horarios_raw.html", "amostra_horarios.html"]
)
raspador = SantaCruz()


def test_transformar_html():
    html = BeautifulSoup(am_hora_raw, "html.parser")

    html_tratado = raspador.tratar_payload_horarios(html)

    print(html_tratado.prettify())

    pass
