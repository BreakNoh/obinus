from bs4 import BeautifulSoup
from obinus.core.tipos import DIAS_UTEIS, Html, Linha, TipoLinha
from obinus.scrapers.grande_floripa.tcbiguacu import TCBiguacu
from pathlib import Path
import utils

PASTA = Path(__file__).parent


def test_extrair_linhas():
    with open(PASTA / "amostra_linhas.html", "r") as amostra:
        soup = BeautifulSoup(amostra.read(), "html.parser")
        linhas = TCBiguacu().extrair_linhas(Html(soup))
        assert len(linhas) == 3
        assert linhas[0][0].tipo == TipoLinha.EXECUTIVO
        assert linhas[1][0].tipo == TipoLinha.EXECUTIVO
        assert linhas[2][0].tipo == TipoLinha.CONVENCIONAL


def test_extrair_horarios():
    with open(PASTA / "amostra_horarios.html", "r") as amostra:
        soup = BeautifulSoup(amostra.read(), "html.parser")
        servicos = TCBiguacu().extrair_horarios(Html(soup))
        assert len(servicos) == 2
        assert len(servicos[0].horarios) == 3
        assert len(servicos[1].horarios) == 1
        assert servicos[0].dias == DIAS_UTEIS
        assert len(servicos[1].horarios[0].obs) == 2

        [utils.checar_horario(s.horarios) for s in servicos]
