from obinus.core.raspador import _extrair
from obinus.core.tipos import Empresa
from obinus.scrapers import RASPADORES_SANTA_CATARINA
from sys import argv


def extrair_empresa(empresa: str | None = None):
    if not empresa:
        if len(argv) > 1:
            alvo = argv[1]
        else:
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


def extrair_regiao(regiao: str | None = None):
    if not regiao:
        if len(argv) > 1:
            alvo = argv[1]
        else:
            print("lista de todas as regioes:")
            [print(regiao) for regiao in RASPADORES_SANTA_CATARINA.keys()]

            alvo = input("\nregião alvo: ")
    else:
        alvo = regiao.lower().strip()

    if not (raspadores := RASPADORES_SANTA_CATARINA.get(alvo)):
        return []

    _extrair(list(raspadores.values()))


def extrair_geral():
    raspadores = []
    [raspadores.extend(list(r.values())) for r in RASPADORES_SANTA_CATARINA.values()]

    _extrair(list(raspadores))
