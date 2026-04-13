from obinus.core.tipos import VALE_DO_ITAJAI
from obinus.scrapers.mobilibus import InterfaceMobilibus


class BluMob(InterfaceMobilibus):
    ID_EMPRESA = "blumob"
    NOME_EMPRESA = "BluMob"
    ID_PROJETO = "5"
    VERSAO_HORARIOS = "2"
    REGIOES = VALE_DO_ITAJAI
