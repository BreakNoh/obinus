from dataclasses import asdict
from pathlib import Path
import csv
import hashlib


from obinus.core.tipos import Empresa


ARQUIVO_ATUAL = Path(__file__).resolve()
DIR_ATUAL = ARQUIVO_ATUAL.parent
DIR_PACOTE = DIR_ATUAL.parent
DIR_RAIZ = DIR_PACOTE.parent.parent
PASTA_SQL = DIR_ATUAL / "sql"
PASTA_OUTPUT = DIR_RAIZ / "output"

PASTA_OUTPUT.mkdir(parents=True, exist_ok=True)


def gerar_rows(empresa: Empresa) -> dict[str, list]:
    rows = {"horarios": [], "servicos": [], "linhas": []}

    for linha in empresa.linhas:
        rows["linhas"].append(
            {
                "id_empresa": empresa.id,
                "id": linha.id,
                "nome": linha.nome,
                "codigo": linha.codigo,
                "detalhe": linha.detalhe,
            }
        )

        for servico in linha.servicos:
            servico_ser = {
                "id_linha": linha.id,
                "id": servico.id,
                "sentido": servico.sentido,
            }
            if not servico_ser in rows["servicos"]:
                rows["servicos"].append(servico_ser)

            for horario in servico.horarios:
                rows["horarios"].append(
                    {"id_servico": servico.id, "id": horario.id, "hora": horario.hora}
                )

    return rows


def gerar_id(identificador: str, prefixo: str) -> str:
    _identificador = identificador.lower().strip()
    _prefixo = prefixo.lower().strip()

    segredo = f"{_prefixo}:{_identificador}"
    hash = hashlib.sha256(segredo.encode()).hexdigest()

    return hash[:8]


def salvar_csv(dados: list, nome_arquivo: str):
    if not dados:
        return

    try:
        cabecalho = asdict(dados[0]).keys()
    except:
        if isinstance(dados[0], dict):
            cabecalho = dados[0].keys()
        else:
            print("erro ao salvar csv")
            return

    try:
        caminho = PASTA_OUTPUT / nome_arquivo
        caminho.parent.mkdir(parents=True, exist_ok=True)

        with open(caminho, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=cabecalho, delimiter=";")

            writer.writeheader()
            for item in dados:
                try:
                    writer.writerow(asdict(item))
                except:
                    if isinstance(item, dict):
                        writer.writerow(item)

        print(f"> {len(dados)} registros salvos em: {nome_arquivo}")
    except Exception as e:
        print(f"X erro ao salvar csv: ", e)
