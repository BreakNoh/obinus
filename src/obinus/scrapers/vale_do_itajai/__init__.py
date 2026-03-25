from .bcbus import BCBus
from .blumob import BluMob
from .consorcio_atalaia import ConsorcioAtalaia
from .expresso_presidente import *
from .nosso_brusque import NossoBrusque
from .onibus_circular import OnibusCircular
from .viacao_praiana import ViacaoPraiana

todos = [
    BCBus(),
    BluMob(),
    ConsorcioAtalaia(),
    ExpressoPresidenteGaspar(),
    ExpressoPresidenteRioMafra(),
    ExpressoPresidenteTimbo(),
    NossoBrusque(),
    OnibusCircular(),
    ViacaoPraiana(),
]

__all__ = ["todos"]
