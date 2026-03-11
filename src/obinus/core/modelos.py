from dataclasses import dataclass


@dataclass
class Linha:
    empresa: str
    codigo: str
    nome: str
    detalhe: str
    executivo: bool
    url: str


@dataclass
class Horario:
    empresa: str
    linha: str
    sentido: str
    hora: str
    dia: str
