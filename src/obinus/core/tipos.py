from dataclasses import dataclass, field
from enum import Enum, auto
import json
from typing import NamedTuple, Final
from bs4 import BeautifulSoup, Tag

type Dias = int
DIAS_UTEIS: Final[int] = 0b0111110
SABADO: Final[int] = 0b0000001
DOMINGO_E_FERIADOS: Final[int] = 0b1000000


class TipoLinha(Enum):
    CONVENCIONAL = auto()
    EXECUTIVO = auto()


type Regioes = int
GRANDE_FLORIPA: Final[Regioes] = 0b100000
SUL: Final[Regioes] = 0b010000
NORTE: Final[Regioes] = 0b001000
VALE_DO_ITAJAI: Final[Regioes] = 0b000100
SERRANA: Final[Regioes] = 0b000010
OESTE: Final[Regioes] = 0b000001


class ObsHorario:
    tipo: str
    valor: str

    def __init__(self, tipo: str, valor: str) -> None:
        self.valor = valor
        self.tipo = tipo

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ObsHorario):
            return False
        return self.tipo == other.tipo and self.valor == other.valor

    def __str__(self) -> str:
        return rf"{{\"tipo:{self.tipo},valor:{self.valor}}}"


class Adaptado(ObsHorario):
    def __init__(self) -> None:
        super().__init__(tipo="ADAPTADO", valor="Veículo com elevador")


class RecolheNoBairo(ObsHorario):
    def __init__(self) -> None:
        super().__init__(tipo="RECOLHE_BAIRRO", valor="Recolhe no bairro")


class MeiaViagem(ObsHorario):
    def __init__(self) -> None:
        super().__init__(tipo="MEIA_VIAGEM", valor="Meia viagem")


class HorarioPrevisto(ObsHorario):
    def __init__(self) -> None:
        super().__init__(tipo="PREVISTO", valor="Horário previsto")


class OperadoPorEmpresa(ObsHorario):
    def __init__(self, empresa: str) -> None:
        super().__init__(tipo="OPERADO_POR", valor=empresa)


class FuncionaDurante(ObsHorario):
    def __init__(self, periodo: str) -> None:
        super().__init__(tipo="DURANTE", valor=periodo)


class ItinerarioDiferenciado(ObsHorario):
    def __init__(self, itinerario: str) -> None:
        super().__init__(tipo="ITINERARIO", valor=itinerario)


class SaidaDe(ObsHorario):
    def __init__(self, local: str) -> None:
        super().__init__(tipo="SAIDA_DE", valor=local)


class Generica(ObsHorario):
    def __init__(self, valor: str, tipo: str = "GENERICA") -> None:
        super().__init__(tipo=tipo, valor=valor)


@dataclass
class Horario:
    hora: str
    obs: list[ObsHorario] = field(default_factory=list)
    id: str | None = None


@dataclass
class Servico:
    dias: Dias = 0
    sentido: str | None = None
    horarios: list[Horario] = field(default_factory=list)
    id: str | None = None


@dataclass
class Linha:
    nome: str
    codigo: str | None = None
    detalhe: str | None = None
    servicos: list[Servico] = field(default_factory=list)
    tipo: TipoLinha = TipoLinha.CONVENCIONAL
    id: str | None = None


@dataclass
class Empresa:
    id: str
    nome: str
    fonte: str | None = None
    linhas: list[Linha] = field(default_factory=list)
    regioes: Regioes = 0


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
