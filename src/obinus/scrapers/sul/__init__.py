from typing import Type
from obinus.core.raspador import InterfaceRaspador
from obinus.scrapers.sul.cribus import CriBus
from obinus.scrapers.sul.expresso_coletivo_icarense import ExpressoColetivoIcarense
from obinus.scrapers.sul.grupo_forquilinhas import GrupoForquilhinhas

RASPADORES_SUL: dict[str, Type[InterfaceRaspador]] = {
    "cribus": CriBus,
    "grupo_forquilinhas": GrupoForquilhinhas,
    "expresso_coletivo_icarense": ExpressoColetivoIcarense,
}
