from obinus.core.tipos import SUL
from obinus.scrapers.mobilibus import InterfaceMobilibus


class CriBus(InterfaceMobilibus):
    ID_EMPRESA = "cribus"
    NOME_EMPRESA = "CriBus"
    ID_PROJETO = "740"
    VERSAO_HORARIOS = "2"
    REGIOES = SUL
    FONTE = "https://www.cribus.com.br"
