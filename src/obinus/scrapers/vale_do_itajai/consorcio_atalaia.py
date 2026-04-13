from obinus.core.tipos import VALE_DO_ITAJAI
from obinus.scrapers.mobilibus import InterfaceMobilibus


class ConsorcioAtalaia(InterfaceMobilibus):
    ID_EMPRESA = "consorcio-atalaia"
    NOME_EMPRESA = "Consórcio Atalaia"
    ID_PROJETO = "391"
    REGIOES = VALE_DO_ITAJAI
