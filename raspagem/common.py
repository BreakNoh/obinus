import re
from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass, asdict
import csv
from pathlib import Path
import requests
from abc import ABC, abstractmethod


@dataclass
class Linha:
    empresa: str
    codigo: str
    nome: str
    detalhe: str
    executivo: bool
    url: str


@dataclass
class Horario:
    empresa: str
    linha: str
    sentido: str
    hora: str
    dia: str


class Raspador(ABC):
    @abstractmethod
    def empresa(self) -> str:
        pass

    @abstractmethod
    def raspar_linhas(self) -> list[Linha]:
        pass

    @abstractmethod
    def raspar_horarios_linha(self, linha: Linha) -> list[Horario]:
        pass


def salvar_csv(dados: list, nome_arquivo: str):
    if not dados:
        print(f"Aviso: A lista para {nome_arquivo} está vazia. Nada foi salvo.")
        return

    cabecalho = asdict(dados[0]).keys()

    try:
        caminho = Path(nome_arquivo)
        caminho.parent.mkdir(parents=True, exist_ok=True)

        with open(caminho, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=cabecalho, delimiter=";")

            writer.writeheader()
            for item in dados:
                writer.writerow(asdict(item))

        print(f"Sucesso! {len(dados)} registros salvos em: {nome_arquivo}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo {nome_arquivo}: {e}")


def normalizar(s: str) -> str:
    s = str(s)
    return re.sub(r"\s+", " ", s).strip()


def extrair_texto(tag: Tag | None):
    if not tag or tag is None:
        return ""
    return normalizar("".join(tag.find_all(string=True, recursive=False)))


sessao = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0"
}


def get_html(url, params: dict = {}) -> tuple[str, int]:
    req = sessao.get(url, params=params, headers=headers)
    if "charset" not in req.headers.get("Content-Type", "").lower():
        req.encoding = req.apparent_encoding
    return (req.text, req.status_code)


def get_soup(url, params: dict = {}) -> tuple[BeautifulSoup, int]:
    html, status = get_html(url, params)
    return (BeautifulSoup(html, "html.parser"), status)
