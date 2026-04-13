from obinus.core.tipos import OESTE
from obinus.scrapers.mobilibus import InterfaceMobilibus


class ColetivoCacador(InterfaceMobilibus):
    ID_EMPRESA = "CCACD"
    NOME_EMPRESA = "Coletivo Caçador"
    ID_PROJETO = "331"
    VERSAO_HORARIOS = "2"
    REGIOES = OESTE
