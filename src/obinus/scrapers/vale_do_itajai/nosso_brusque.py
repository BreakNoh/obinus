from obinus.core.tipos import VALE_DO_ITAJAI
from obinus.scrapers.mobilibus import InterfaceMobilibus


class ConsorcioNossoBrusque(InterfaceMobilibus):
    NOME_EMPRESA = "Consórcio Nosso Brusque"
    ID_PROJETO = "8"
    VERSAO_HORARIOS = "2"
    REGIOES = VALE_DO_ITAJAI
