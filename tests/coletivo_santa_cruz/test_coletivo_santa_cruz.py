from utils import *
from obinus.scrapers.norte.santa_cruz import SantaCruz, QUERY_LINHAS, Tratador

amostras_raw = carregar(
    Path(__file__).parent,
    [
        "amostras/_amostra_raw_0.html",
        "amostras/_amostra_raw_1.html",
        "amostras/_amostra_raw_2.html",
    ],
)
amostras_san = carregar(
    Path(__file__).parent,
    [
        "amostras/amostra_san_0.html",
        "amostras/amostra_san_1.html",
        "amostras/amostra_san_2.html",
    ],
)
raspador = SantaCruz()


def test_transformar_html():
    for i in range(3):
        html_raw = BeautifulSoup(amostras_raw[i], "html.parser")
        html_san = BeautifulSoup(amostras_san[i], "html.parser")

        html_tratado_raw = Tratador().tratar_payload_horarios(html_raw)
        html_tratado_san = Tratador().tratar_payload_horarios(html_san)

        print(f"==== amostra_raw{i} =====")
        print(html_tratado_raw.prettify())
        print(f"==== amostra_san{i} =====")
        print(html_tratado_san.prettify())
        print(f"==========================")
