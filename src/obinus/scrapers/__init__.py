from typing import Type
from obinus.core.raspador import InterfaceRaspador
from obinus.scrapers.grande_floripa import RASPADORES_GRANDE_FLORIPA
from obinus.scrapers.norte import RASPADORES_NORTE
from obinus.scrapers.oeste import RASPADORES_OESTE
from obinus.scrapers.serrana import RASPADORES_SERRANA
from obinus.scrapers.sul import RASPADORES_SUL
from obinus.scrapers.vale_do_itajai import RASPADORES_VALE_DO_ITAJAI

RASPADORES_SANTA_CATARINA: dict[str, dict[str, Type[InterfaceRaspador]]] = {
    "grande-floripa": RASPADORES_GRANDE_FLORIPA,
    "vale-do-itajai": RASPADORES_VALE_DO_ITAJAI,
    "norte": RASPADORES_NORTE,
    "sul": RASPADORES_SUL,
    "serrana": RASPADORES_SERRANA,
    "oeste": RASPADORES_OESTE,
}
