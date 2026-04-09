from obinus.scrapers.grande_floripa import RASPADORES_GRANDE_FLORIPA
from obinus.scrapers.norte import RASPADORES_NORTE
from obinus.scrapers.oeste import RASPADORES_OESTE
from obinus.scrapers.serrana import RASPADORES_SERRANA
from obinus.scrapers.sul import RASPADORES_SUL
from obinus.scrapers.vale_do_itajai import RASPADORES_VALE_DO_ITAJAI
from obinus.scrapers.mobilibus import InterfaceMobilibus

RASPADORES_SANTA_CATARINA = {
    **RASPADORES_GRANDE_FLORIPA,
    **RASPADORES_VALE_DO_ITAJAI,
    **RASPADORES_NORTE,
    **RASPADORES_SUL,
    **RASPADORES_SERRANA,
    **RASPADORES_OESTE,
}
