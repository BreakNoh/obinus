from obinus.core.tipos import VALE_DO_ITAJAI
from obinus.scrapers.mobilibus import InterfaceMobilibus


class ConsorcioNossoBrusque(InterfaceMobilibus):
    ID_EMPRESA = "consorcio-nosso-brusque"
    NOME_EMPRESA = "Consórcio Nosso Brusque"
    ID_PROJETO = "8"
    VERSAO_HORARIOS = "2"
    REGIOES = VALE_DO_ITAJAI
