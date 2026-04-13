from typing import Type
from obinus.core.raspador import InterfaceRaspador
from obinus.core.tipos import Empresa
from obinus.scrapers import RASPADORES_SANTA_CATARINA
from obinus.utils.salvar import gerar_rows, salvar_csv
from concurrent.futures import ThreadPoolExecutor, as_completed


def _processar_raspador(raspador: InterfaceRaspador) -> Empresa:
    empresa = raspador.raspar()
    rows = gerar_rows(empresa)
    for lista, valores in rows.items():
        salvar_csv(valores, f"{empresa.id}_{lista}.csv".lower())

    return empresa


def _extrair(
    raspadores: list[Type[InterfaceRaspador]], _async: bool = True
) -> list[Empresa]:

    if not _async:
        return [_processar_raspador(r()) for r in raspadores]

    empresas = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(_processar_raspador, r()) for r in raspadores]

        for future in as_completed(futures):
            try:
                empresa = future.result()
                empresas.append(empresa)
            except Exception as e:
                print(f"erro: {e} \n")

    return empresas


def extrair_empresa(empresa: str | None = None):
    if not empresa:
        print("lista de todas as empresas:")
        [
            [print(empresa) for empresa in regiao.keys()]
            for regiao in RASPADORES_SANTA_CATARINA.values()
        ]

        alvo = input("\nempresa alvo: ")
    else:
        alvo = empresa.lower().strip()

    for regiao in RASPADORES_SANTA_CATARINA.values():
        for empresa, raspador in regiao.items():
            if empresa.lower() == alvo.strip().lower():
                _extrair([raspador], False)[0]
                return


def extrair_regiao(regiao: str | None = None) -> list[Empresa]:
    if not regiao:
        print("lista de todas as regioes:")
        [print(regiao) for regiao in RASPADORES_SANTA_CATARINA.keys()]

        alvo = input("\nregião alvo: ")
    else:
        alvo = regiao.lower().strip()

    if not (raspadores := RASPADORES_SANTA_CATARINA.get(alvo)):
        return []

    return _extrair(list(raspadores.values()), True)


def extrair_geral() -> list[Empresa]:
    raspadores = []
    [raspadores.extend(list(r.values())) for r in RASPADORES_SANTA_CATARINA.values()]

    return _extrair(list(raspadores), True)
