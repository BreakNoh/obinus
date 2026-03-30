from dataclasses import dataclass, field
from enum import Enum, auto
from typing import NamedTuple, Final
from bs4 import BeautifulSoup, Tag

type Dias = int
DIAS_UTEIS: Final[int] = 0b0111110
SABADO: Final[int] = 0b0000001
DOMINGO_E_FERIADOS: Final[int] = 0b1000000


class TipoLinha(Enum):
    CONVENCIONAL = auto()
    EXECUTIVO = auto()


@dataclass(frozen=True)
class Adaptado: ...


@dataclass(frozen=True)
class OperadoPor:
    empresa: str


@dataclass(frozen=True)
class RecolheBairro: ...


@dataclass(frozen=True)
class MeiaViagem: ...


@dataclass(frozen=True)
class HorarioPrevisto: ...


@dataclass(frozen=True)
class ItinerarioDiferenciado:
    itinerario: str


@dataclass(frozen=True)
class Generica:
    tipo: str | None = None
    valor: str | None = None


@dataclass(frozen=True)
class SaidaDe:
    said: str


ObsHorario = (
    Adaptado
    | ItinerarioDiferenciado
    | MeiaViagem
    | HorarioPrevisto
    | OperadoPor
    | RecolheBairro
    | SaidaDe
    | Generica
)


@dataclass
class Horario:
    hora: str
    obs: list[ObsHorario] = field(default_factory=list[ObsHorario])


@dataclass
class Servico:
    dias: Dias = 0
    sentido: str | None = None
    horarios: list[Horario] = field(default_factory=list[Horario])


@dataclass
class Linha:
    nome: str
    codigo: str | None = None
    detalhe: str | None = None
    servicos: list[Servico] = field(default_factory=list[Servico])
    tipo: TipoLinha = TipoLinha.CONVENCIONAL


class Html(NamedTuple):
    html: BeautifulSoup | Tag


class Json(NamedTuple):
    json: object


class Url(NamedTuple):
    url: str


class Raw(NamedTuple):
    valor: str


Busca = Url | Html | Raw | None
Payload = Html | Json | Raw | None
