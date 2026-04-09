from obinus.scrapers.sul.cribus import CriBus
from obinus.scrapers.sul.expresso_coletivo_icarense import ExpressoColetivoIcarense
from obinus.scrapers.sul.grupo_forquilinhas import GrupoForquilhinhas

RASPADORES_SUL = {
    "cribus": CriBus,
    "grupo_forquilinhas": GrupoForquilhinhas,
    "expresso_coletivo_icarense": ExpressoColetivoIcarense,
}
