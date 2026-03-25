from .biguacu import Biguacu
from .fenix import Fenix
from .jotur import Jotur
from .estrela import Estrela
from .imperatriz import Imperatriz
from .santa_terezinha import SantaTerezinha

todos = [Biguacu(), Fenix(), Jotur(), Estrela(), Imperatriz(), SantaTerezinha()]

__all__ = [
    "todos",
    "Biguacu",
    "Fenix",
    "Jotur",
    "Estrela",
    "Imperatriz",
    "SantaTerezinha",
]
