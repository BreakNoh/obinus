from dataclasses import dataclass
from typing import NamedTuple, Protocol, Union
from obinus.utils.http import get_json, get_soup

from bs4 import BeautifulSoup
from .modelos import Dias, Linha, Horario
from abc import ABC, abstractmethod
from time import sleep
import random

MIN_DELAY = 0.1
MAX_DELAY = 0.5


class _Raspador(Protocol):
    def extrair_linhas(self, payload: BeautifulSoup | dict) -> list: ...
    def extrair_horarios(self, payload: BeautifulSoup | dict) -> list: ...


class _Cliente(Protocol):
    def buscar_linhas(self, payload: str | None) -> BeautifulSoup | dict: ...
    def buscar_horario(self, payload: str | None) -> BeautifulSoup | dict: ...


class Json(NamedTuple):
    url: str
    metodo: str = "GET"
    params: dict[str, str] | None = None
    headers: dict[str, str] | None = None
    data: dict[str, str] | str | None = None


class Html(NamedTuple):
    url: str
    metodo: str = "GET"
    params: dict[str, str] | None = None
    headers: dict[str, str] | None = None
    data: dict[str, str] | str | None = None


class Raw(NamedTuple):
    raw: Payload


MetodoBusca = Union[Json, Html, Raw]
type Payload = BeautifulSoup | object


class Raspador(ABC):
    NOME_EMPRESA: str = "EMPRESA"

    METODO_EXTRACAO_LINHAS: MetodoBusca
    METODO_EXTRACAO_HORARIOS: MetodoBusca

    def empresa(self) -> str:
        return self.NOME_EMPRESA

    def buscar(self, busca: MetodoBusca) -> Payload | None:
        match busca:
            case Json(url, metodo, params, headers, data):
                if resultado := get_json(
                    url=url, params=params, headers=headers, metodo=metodo, data=data
                ):
                    return resultado[0]

            case Html(url, metodo, params, headers, data):
                if resultado := get_soup(
                    url=url, params=params, headers=headers, metodo=metodo, data=data
                ):
                    return resultado[0]
            case Raw(raw):
                return raw

    def buscar_linhas(self) -> Payload | None:
        return self.buscar(self.METODO_EXTRACAO_LINHAS)

    def buscar_horarios(self, metodo: MetodoBusca) -> Payload | None:
        return self.buscar(metodo)

    @abstractmethod
    def extrair_linhas(self, payload: Payload) -> list[Linha]: ...
    @abstractmethod
    def extrair_horarios(self, payload: Payload) -> list[Horario]: ...
    @abstractmethod
    def converter_dias(self, d: str) -> Dias: ...

    @abstractmethod
    def raspar_linhas(self) -> list[Linha]: ...
    @abstractmethod
    def raspar_horarios_linha(self, linha: Linha) -> list[Horario]: ...

    def raspar_horarios(self, linhas: list[Linha]) -> list[Horario]:
        horarios = []
        for linha in linhas:
            horarios_raspados = self.raspar_horarios_linha(linha)

            horarios.extend(horarios_raspados)
        return horarios

    def esperar(self):
        sleep(random.uniform(MIN_DELAY, MAX_DELAY))

    def normalizar_dia(self, d: str) -> str | list[str]:
        return d

    def raspar(self) -> tuple[list[Linha], list[Horario]]:
        linhas, horarios = [], []

        payload_linhas = self.buscar_linhas()
        linhas = self.extrair_linhas(payload_linhas)

        for linha in linhas:
            payload_horarios = self.buscar_horarios(linha.nome)
            horarios.extend(self.extrair_horarios(payload_horarios))

        return linhas, horarios
