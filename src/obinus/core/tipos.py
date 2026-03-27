from dataclasses import dataclass
from enum import Enum, auto
from typing import NamedTuple, Final
from bs4 import BeautifulSoup

type Dias = int
DIAS_UTEIS: Final[int] = 0b0111110
SABADO: Final[int] = 0b0000001
DOMINGO_E_FERIADOS: Final[int] = 0b1000000


class TipoLinha(Enum):
    CONVENCIONAL = auto()
    EXECUTIVO = auto()


@dataclass
class Linha_:
    nome: str
    codigo: str | None = None
    servicos: list[Servico] = []
    tipo: TipoLinha = TipoLinha.CONVENCIONAL


@dataclass
class Servico:
    dias: Dias = 0
    sentido: str | None = None
    horarios: list[Horario_] = []


@dataclass
class Horario_:
    hora: str
    obs: list[str] | None = None


class Html(NamedTuple):
    html: BeautifulSoup


class Json(NamedTuple):
    json: object


class Url(NamedTuple):
    url: str


class Raw(NamedTuple):
    valor: str


Busca = Url | Html | None
Payload = Html | Json | Raw | None
