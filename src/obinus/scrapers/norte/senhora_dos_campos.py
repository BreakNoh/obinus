from obinus.core.tipos import NORTE
from obinus.scrapers.mobilibus import InterfaceMobilibus


class SenhoraDosCampos(InterfaceMobilibus):
    ID_EMPRESA = "senhora-dos-campos"
    ID_PROJETO = "816"
    NOME_EMPRESA = "Senhora dos Campos"
    REGIOES = NORTE
    FONTE = "https://www.senhoradoscampos.com.br"
