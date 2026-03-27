from abc import ABC
from typing import Generic, Protocol, TypeVar
from obinus.core.tipos import *

P = TypeVar("P", bound=Payload)
Q = TypeVar("Q", bound=Payload)
B = TypeVar("B", bound=Busca)


class Extrator(Protocol, Generic[P, Q, B]):
    def extrair_linhas(self, payload: P) -> list[tuple[Linha_, B]]: ...
    def extrair_horarios(self, payload: Q) -> list[Servico]: ...


class Buscador(Protocol, Generic[P, Q, B]):
    def buscar_linhas(self) -> P: ...
    def buscar_horarios(self, busca: B) -> Q: ...


class InterfaceRaspador(
    ABC, Extrator[P, Q, B], Buscador[P, Q, B], Generic[P, Q, B]
): ...


def raspar(extrator: Extrator[P, Q, B], buscador: Buscador[P, Q, B]) -> list[Linha_]:
    payload_linhas = buscador.buscar_linhas()
    resultado_linhas = extrator.extrair_linhas(payload_linhas)

    for linha, busca in resultado_linhas:
        payload_horarios = buscador.buscar_horarios(busca)

        horarios = extrator.extrair_horarios(payload_horarios)

    return []  # só mockup
