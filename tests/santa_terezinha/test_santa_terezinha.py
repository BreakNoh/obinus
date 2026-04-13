from bs4 import BeautifulSoup
from obinus.core.tipos import Html
from obinus.scrapers.grande_floripa.santa_terezinha import SantaTerezinha
from pathlib import Path

import utils

PASTA_ATUAL = Path(__file__).parent
AMOSTRA_HORARIOS = PASTA_ATUAL / "amostra_horarios.html"
AMOSTRA_LINHAS = PASTA_ATUAL / "amostra_linhas.html"


def test_extrair_linhas():
    with open(AMOSTRA_LINHAS, "r") as a:
        amostra = a.read()
        html = Html(BeautifulSoup(amostra, "html.parser"))

        linhas = SantaTerezinha().extrair_linhas(html)

        assert len(linhas) == 3


def test_extrair_horarios():
    with open(AMOSTRA_HORARIOS, "r") as a:
        amostra = a.read()
        html = Html(BeautifulSoup(amostra, "html.parser"))

        servicos = SantaTerezinha().extrair_horarios(html)
        legendas = SantaTerezinha().extrair_legenda(html.html)

        assert len(servicos) == 1
        assert len(servicos[0].horarios) == 3
        assert len(legendas) == 3

        for hor in servicos[0].horarios:
            assert len(hor.obs) == 1

        [utils.checar_horario(s.horarios) for s in servicos]
