from dataclasses import dataclass
from typing import Any


@dataclass
class Linha:
    empresa: str
    codigo: str
    nome: str
    detalhe: str
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
