from typing import Type
from obinus.core.raspador import InterfaceRaspador
from obinus.scrapers.oeste.coletivo_cacador import ColetivoCacador

RASPADORES_OESTE: dict[str, Type[InterfaceRaspador]] = {
    "coletivo_cacador": ColetivoCacador
}
