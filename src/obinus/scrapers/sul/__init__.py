from .cribus import CriBus
from .expresso_icarense import ExpressoIcarense
from .grupo_forquilinhas import GrupoForquilhinha

todos = [CriBus(), ExpressoIcarense(), GrupoForquilhinha()]

__all__ = ["todos"]
