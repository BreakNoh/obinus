import sys

from dataclasses import asdict
from functools import reduce
from typing import Type

from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

from obinus.core.tipos import *
from obinus.utils.salvar import (
    salvar_json,
)
from obinus.utils.transformacao import (
    adicionar_slug,
    encurtar_nome,
    extrair_detalhe_nome,
    normalizar_nome,
)
from obinus.core.raspador import InterfaceRaspador


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

    transformacoes = [
        normalizar_nome,
        adicionar_slug,
        extrair_detalhe_nome,
        encurtar_nome,
    ]

    empresa = reduce(lambda emp, trans: trans(emp), transformacoes, empresa)

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
            "slug": f"{dados_empresa['slug']}/{l['slug']}",
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
