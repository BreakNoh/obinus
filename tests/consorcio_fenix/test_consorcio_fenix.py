from bs4 import BeautifulSoup
from pathlib import Path
from obinus.core.tipos import DIAS_UTEIS, DOMINGO_E_FERIADOS, SABADO, Adaptado, Html
from obinus.scrapers.grande_floripa.consorcio_fenix import ConsorcioFenix

dir_atual = Path(__file__).parent
raspador = ConsorcioFenix()


def test_raspar_horarios():
    with open(dir_atual / "amostra_horarios.html", "r") as arq:
        amostra_horarios = BeautifulSoup(arq.read(), "html.parser")

        servicos = raspador.extrair_horarios(Html(amostra_horarios))

        assert len(servicos) == 3
        [sa, sb, sc] = servicos
        assert sa.dias == DOMINGO_E_FERIADOS
        assert sa.sentido == "A"
        assert len(sa.horarios) == 1
        assert sa.horarios[0].obs[0] == Adaptado()

        assert sb.dias == SABADO
        assert sb.sentido == "B"
        assert len(sb.horarios) == 2

        assert sc.dias == DIAS_UTEIS
        assert sc.sentido == "C"
        assert len(sa.horarios) == 1


def test_raspar_linhas():
    with open(dir_atual / "amostra_linhas.html", "r") as arq:
        amostra_linhas = BeautifulSoup(arq.read(), "html.parser")

        linhas = raspador.extrair_linhas(Html(amostra_linhas))

        assert len(linhas) == 3
        [(la, _), (lb, _), (lc, _)] = linhas
        assert la.codigo == "665"
        assert la.nome == "Abraão"
        assert lb.codigo == "762"
        assert lb.nome == "Angelo Laporta"
        assert lc.codigo == "844"
        assert lc.nome == "Bairro de Fátima"
