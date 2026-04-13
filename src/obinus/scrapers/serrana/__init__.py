from typing import Type
from obinus.core.raspador import InterfaceRaspador
from obinus.scrapers.serrana.transul import Transul

RASPADORES_SERRANA: dict[str, Type[InterfaceRaspador]] = {"transul": Transul}
