from obinus.core.tipos import VALE_DO_ITAJAI
from obinus.scrapers.mobilibus import InterfaceMobilibus


class OnibusCircular(InterfaceMobilibus):
    NOME_EMPRESA = "Ônibus Circular"
    ID_PROJETO = "821"
    VERSAO_HORARIOS = "2"
    REGIOES = VALE_DO_ITAJAI
