from dataclasses import asdict
import sys
import time
import random

from abc import ABC, abstractmethod
from typing import Type
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from typing import Callable, Generic, Protocol, TypeVar

from obinus.core.tipos import *
from obinus.utils.salvar import (
    criar_slug,
    identificar,
    normalizar,
    salvar_json,
)

P = TypeVar("P", bound=Payload)
Q = TypeVar("Q", bound=Payload)
B = TypeVar("B", bound=Busca)


def _serializar_linha(linha: Linha):
    dados_linha = asdict(linha)

    servicos_ser = {}

    for s in dados_linha["servicos"]:
        dia = str(s["dias"])

        if not servicos_ser.get(dia):
            servicos_ser[dia] = []

        servicos_ser[dia].append({"sentido": s["sentido"], "horarios": s["horarios"]})

    dados_linha["servicos"] = servicos_ser

    return dados_linha


def _processar_raspador(
    raspador: InterfaceRaspador, atualizar_progresso: Callable[[int]] | None = None
) -> Empresa:
    empresa = raspador.raspar(atualizar_progresso)

    # data = time.strftime("%Y%m%d", time.localtime())

    for linha in empresa.linhas:
        salvar_json(_serializar_linha(linha), f"{empresa.slug}/{linha.slug}.json")

    dados_empresa = asdict(empresa)
    del dados_empresa["id"]
    dados_empresa["linhas"] = [
        {
            "nome_linha": l["nome"],
            "codigo_linha": l["codigo"],
            "nome_empresa": dados_empresa["nome"],
        }
        for l in dados_empresa["linhas"]
    ]

    salvar_json(dados_empresa, f"{empresa.slug}/_self.json")

    return empresa


def _extrair(
    raspadores: list[Type[InterfaceRaspador]], _async: bool = True
) -> list[Empresa]:
    instancias = [r() for r in raspadores]
    empresas = []
    total_linhas = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(ins._raspar_linhas) for ins in instancias]

        for future in as_completed(futures):
            try:
                linhas = future.result()
                total_linhas += len(linhas)

            except Exception as e:
                print(f"erro: {e} \n")

    if any(arg in ["--contagem-linhas", "--contar", "-c"] for arg in sys.argv):
        print(total_linhas)
        exit(0)

    with tqdm(
        total=total_linhas, desc="Linhas raspadadas", unit="lin"
    ) as barra_progresso:
        atualizar_progresso = lambda n=1: barra_progresso.update(n)

        if not _async:
            return [_processar_raspador(ins, atualizar_progresso) for ins in instancias]

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(_processar_raspador, ins, atualizar_progresso)
                for ins in instancias
            ]

            for future in as_completed(futures):
                try:
                    empresa = future.result()
                    empresas.append(empresa)

                except Exception as e:
                    print(f"erro: {e} \n")

    print(_sumario(empresas))
    return empresas


def _sumario(empresas: list[Empresa]) -> str:
    contagem = {"empresas": len(empresas), "linhas": 0, "servicos": 0, "horarios": 0}

    for emp in empresas:
        contagem["linhas"] += len(emp.linhas)

        for lin in emp.linhas:
            contagem["servicos"] += len(lin.servicos)

            for ser in lin.servicos:
                contagem["horarios"] += len(ser.horarios)

    resultado = "Sumário da raspagem:"

    for k, v in contagem.items():
        resultado += f"\n\t> {k}: {v}"

    return resultado


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
                normalizar(linha)
                identificar(linha)

                linhas_finalizadas.append(linha)
                if atualizar_progresso:
                    atualizar_progresso(1)

            except Exception as e:
                print(f"erro ao raspar {empresa.nome} | {linha.nome}:", e)

        empresa.linhas = linhas_finalizadas
        empresa.slug = criar_slug(empresa.nome)

        return empresa
