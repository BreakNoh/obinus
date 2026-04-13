from typing import Type

from obinus.core.raspador import InterfaceRaspador
from .tcbiguacu import TCBiguacu
from .tcimperatriz import TCImperatriz
from .tcestrela import TCEstrela
from .consorcio_fenix import ConsorcioFenix
from .jotur import Jotur
from .santa_terezinha import SantaTerezinha

RASPADORES_GRANDE_FLORIPA: dict[str, Type[InterfaceRaspador]] = {
    "tcbiguacu": TCBiguacu,
    "tcimperatriz": TCImperatriz,
    "tcestrela": TCEstrela,
    "consorcio_fenix": ConsorcioFenix,
    "jotur": Jotur,
    "santa_terezinha": SantaTerezinha,
}
