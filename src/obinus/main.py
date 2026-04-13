from obinus.core.tipos import Empresa
from obinus.scrapers import RASPADORES_SANTA_CATARINA


def extrair_regiao(regiao: str) -> list[Empresa]:
    if not (raspadores := RASPADORES_SANTA_CATARINA.get(regiao)):
        return []

    empresas = []

    for e, r in raspadores.items():
        pass

    return empresas
