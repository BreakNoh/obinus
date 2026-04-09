from obinus.core.tipos import VALE_DO_ITAJAI
from obinus.scrapers.mobilibus import InterfaceMobilibus


class ConsorcioAtalaia(InterfaceMobilibus):
    NOME_EMPRESA = "Consórcio Atalaia"
    ID_PROJETO = "391"
    REGIOES = VALE_DO_ITAJAI
