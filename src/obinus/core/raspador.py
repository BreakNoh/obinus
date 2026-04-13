from abc import ABC, abstractmethod
from typing import Generic, Protocol, TypeVar
from obinus.core.tipos import *
from obinus.utils.salvar import gerar_id
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
    @abstractmethod
    def empresa(self) -> Empresa: ...

    def _esperar(self):
        MAX_DELAY = 1
        MIN_DELAY = 0.5

        sleep(uniform(MIN_DELAY, MAX_DELAY))

    def raspar(self) -> Empresa:
        empresa = self.empresa()
        linhas = []

        payload_linhas = self.buscar_linhas()
        resultado_linhas = self.extrair_linhas(payload_linhas)

        for linha, busca in resultado_linhas:
            try:
                self._esperar()
                payload_horarios = self.buscar_horarios(busca)

                servicos = self.extrair_horarios(payload_horarios)
                linha.id = gerar_id(linha.codigo or linha.nome, empresa.id)

                for servico in servicos:
                    servico.id = gerar_id(servico.sentido or "", linha.id)

                    for horario in servico.horarios:
                        horario.id = gerar_id(horario.hora, servico.id)

                linha.servicos = servicos

                linhas.append(linha)
            except Exception as e:
                print(e)

        empresa.linhas = linhas

        return empresa
