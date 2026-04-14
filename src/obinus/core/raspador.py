from abc import ABC, abstractmethod
import re
from typing import Callable, Generic, Protocol, TypeVar
from obinus.core.tipos import *
from obinus.utils.salvar import gerar_id, identificar, normalizar
from time import sleep
from random import uniform

P = TypeVar("P", bound=Payload)
Q = TypeVar("Q", bound=Payload)
B = TypeVar("B", bound=Busca)


class Extrator(Protocol, Generic[P, Q, B]):
    def extrair_linhas(self, payload: P) -> list[tuple[Linha, B]]: ...
    def extrair_horarios(self, payload: Q) -> list[Servico]: ...


class Buscador(Protocol, Generic[P, Q, B]):
    def buscar_linhas(self) -> P: ...
    def buscar_horarios(self, busca: B) -> Q: ...


class InterfaceRaspador(ABC, Extrator[P, Q, B], Buscador[P, Q, B], Generic[P, Q, B]):
    _cache_linhas: list[tuple[Linha, B]] | None = None

    @abstractmethod
    def empresa(self) -> Empresa: ...

    def _esperar(self, min: float = 0.5, max: float = 1.5):
        sleep(uniform(min, max))

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
                normalizar(linha)
                identificar(linha, empresa.id)

                linhas_finalizadas.append(linha)
                if atualizar_progresso:
                    atualizar_progresso(1)

            except Exception as e:
                print(f"erro ao raspar {empresa.nome} | {linha.nome}:", e)

        empresa.linhas = linhas_finalizadas

        return empresa
