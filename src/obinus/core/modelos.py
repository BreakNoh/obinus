from dataclasses import dataclass
from typing import Any, Final

# D S T Q Q S S
DIAS_UTEIS: Final[int] = 0b0111110
SABADO: Final[int] = 0b0000001
DOMINGO_E_FERIADOS: Final[int] = 0b1000000
type Dias = int


@dataclass
class _Empresa:
    nome: str
    linhas: list[Linha]
    urls: list[str] = []


@dataclass
class _Linha:
    nome: str
    horarios: list[_Horarios]
    itinerarios: list[_Itinerario] = []
    codigo: str | None = None
    observacoes: list[str] = []
    executivo: bool = False
    urls: list[str] = []


@dataclass
class _Itinerario:
    ruas: list[str]


@dataclass
class _Horarios:
    sentido: str
    dias: str
    horarios: list[_Horario] = []


@dataclass
class _Horario:
    hora: str
    observacoes: list[str]


@dataclass
class Linha:
    empresa: str
    codigo: str
    nome: str
    detalhe: str = ""
    executivo: bool = False
    url: str = ""

    metadados: Any = None


@dataclass
class Horario:
    empresa: str
    linha: str
    sentido: str
    hora: str
    dia: str | list[str]

    metadados: Any = None
