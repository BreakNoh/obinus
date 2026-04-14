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

    def _esperar(self):
        MAX_DELAY = 1
        MIN_DELAY = 0.5

        sleep(uniform(MIN_DELAY, MAX_DELAY))

    def _raspar_linhas(self) -> list[tuple[Linha, B]]:
        payload_linhas = self.buscar_linhas()

        if self._cache_linhas is None:
            self._cache_linhas = self.extrair_linhas(payload_linhas)
        return self._cache_linhas

    def _raspar_horarios(self, busca: B) -> list[Servico]:
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
                if isinstance(busca, Url):
                    self._esperar()

                linha.servicos = self._raspar_horarios(busca)
                normalizar(linha)
                identificar(linha, empresa.id)

                linhas_finalizadas.append(linha)
                if atualizar_progresso:
                    atualizar_progresso(1)
            except Exception as e:
                print(f"erro ao raspar {linha.nome}:", e)

        empresa.linhas = linhas_finalizadas

        return empresa
