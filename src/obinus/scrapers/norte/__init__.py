from typing import Type
from obinus.core.raspador import InterfaceRaspador
from .coletivo_rainha import ColetivoRainha
from .gidion_transtusa import GidionTranstusa
from .senhora_dos_campos import SenhoraDosCampos
from .coletivo_santa_cruz import ColetivoSantaCruz


RASPADORES_NORTE: dict[str, Type[InterfaceRaspador]] = {
    "coletivo_rainha": ColetivoRainha,
    "gidion_transtusa": GidionTranstusa,
    "senhora_dos_campos": SenhoraDosCampos,
    "coletivo_santa_cruz": ColetivoSantaCruz,
}
