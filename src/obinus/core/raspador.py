import time
import random

from abc import ABC, abstractmethod
from typing import Callable, Generic, Protocol, TypeVar, runtime_checkable
from obinus.core.tipos import *

P = TypeVar("P", bound=Payload)
Q = TypeVar("Q", bound=Payload)
B = TypeVar("B", bound=Busca)


class Extrator(Protocol, Generic[P, Q, B]):
    def extrair_linhas(self, payload: P) -> list[tuple[Linha, B]]: ...
    def extrair_horarios(self, payload: Q) -> list[Servico]: ...


class Buscador(Protocol, Generic[P, Q, B]):
    def buscar_linhas(self) -> P: ...
    def buscar_horarios(self, busca: B) -> Q: ...


# raspagem de itinerario
@runtime_checkable
class BuscadorItinerario[B: Busca, P: Payload](Protocol):
    def buscar_itinerarios(self, busca: B) -> P: ...


@runtime_checkable
class ExtratorItinerario[P: Payload](Protocol):
    def extrair_itinerarios(self, payload: P) -> dict[str, list[str]]: ...


class InterfaceRaspador(ABC, Extrator[P, Q, B], Buscador[P, Q, B], Generic[P, Q, B]):
    _cache_linhas: list[tuple[Linha, B]] | None = None

    @abstractmethod
    def empresa(self) -> Empresa: ...

    def _esperar(self, min: float = 1, max: float = 1.5):
        time.sleep(random.uniform(min, max))

    def _raspar_linhas(self) -> list[tuple[Linha, B]]:
        if self._cache_linhas is None:
            self._esperar()
            payload_linhas = self.buscar_linhas()
            self._cache_linhas = self.extrair_linhas(payload_linhas)

        return self._cache_linhas

    def _raspar_horarios(self, busca: B) -> list[Servico]:
        if isinstance(busca, Url):
            self._esperar()

        payload_horarios = self.buscar_horarios(busca)
        return self.extrair_horarios(payload_horarios)

    def raspar(
        self,
        atualizar_progresso: Callable[[int]] | None = None,
    ) -> Empresa:
        empresa = self.empresa()

        linhas = self._raspar_linhas()
        linhas_finalizadas = []

        for linha, busca in linhas:
            try:
                linha.servicos = self._raspar_horarios(busca)
                # normalizar(linha)
                # identificar(linha)

                linhas_finalizadas.append(linha)
                if atualizar_progresso:
                    atualizar_progresso(1)

            except Exception as e:
                print(f"erro ao raspar {empresa.nome} | {linha.nome}:", e)

        empresa.linhas = linhas_finalizadas
        # empresa.slug = criar_slug(empresa.nome)

        return empresa
