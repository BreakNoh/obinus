import re
from pprint import pp
import requests
from bs4 import BeautifulSoup
from obinus.core.base import Raspador
from obinus.utils.texto import extrair_texto
from obinus.core.modelos import Linha, Horario
from pathlib import Path

from obinus.utils.http import HEADERS_BASE, get_soup

ARQUIVO_ATUAL = Path(__file__)
PASTA_ATUAL = ARQUIVO_ATUAL.parent
ARQUIVO_PAYLOAD = PASTA_ATUAL / "body_praiana.txt"

URL_HORARIOS = "https://praiana.com.br/wp-admin/admin-ajax.php"
URL_LINHAS = "https://praiana.com.br/horarios/"


class ViacaoPraiana(Raspador):
    NOME_EMPRESA = "VIACAO_PRAIANA"
    _payload: str | None = None

    def raspar_linhas(self) -> list[Linha]:
        soup, status = get_soup(URL_LINHAS)
        linhas = []

        for opt in soup.select("select[name='linhas'] option[value!='']"):
            nome = extrair_texto(opt)
            codigo = opt.get("value")

            if not nome or not codigo:
                continue

            linha = Linha(
                empresa=self.NOME_EMPRESA, nome=nome, codigo=str(codigo), detalhe=""
            )

            linhas.append(linha)

        return linhas

    def normalizar_dia(self, d: str) -> str | list[str]:
        d_norm = d.lower().strip()
        dias = []
        if "sex" in d_norm and "seg" in d_norm:
            dias.append("UTIL")
        if "sáb" in d_norm:
            dias.append("SABADO")
        if "feri" in d_norm and "domi" in d_norm:
            dias.append("DOMINGO_FERIADO")
        return dias if len(dias) > 0 else "UTIL"

    def _carregar_payload(self) -> bool:
        try:
            self._payload = open(ARQUIVO_PAYLOAD, "r").read().replace("\n", "&")
            return True
        except Exception as e:
            print("x erro ao carregar arquivo payload", e)
            return False

    def _carregar_html(self, codigo: str) -> BeautifulSoup | None:

        if not self._payload:
            if not self._carregar_payload():
                return None

        if self._payload is None:
            return None

        payload = self._payload % codigo
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://praiana.com.br/horarios/",
        }
        req = requests.post(URL_HORARIOS, data=payload, headers=HEADERS_BASE | headers)

        if req.status_code != 200:
            pp(req.raw)
            return None

        json = req.json()
        if not json["content"]:
            pp(json)
            return None

        return BeautifulSoup(json["content"], "html.parser")

    def raspar_horarios_linha(self, linha: Linha) -> list[Horario]:
        soup = self._carregar_html(linha.codigo)
        padrao_hora = r"(\d{2}:\d{2})"

        if not soup:
            return []

        horarios = []

        sentido: str | None = None
        dia: str | list[str] | None = None

        for tag in soup.select("div, span"):
            texto = extrair_texto(tag)

            if texto == "":
                continue

            texto_norm = texto.strip().lower()

            if re.match(r"R$", texto_norm):
                continue

            if (
                "rua" in texto_norm
                or "av" in texto_norm
                or "sem horários" in texto_norm
            ):
                continue

            if not re.match(padrao_hora, texto_norm):
                sentido = texto.strip()
                dia = self.normalizar_dia(sentido)

                sentido = re.sub(r"(\s+-\s+)?\(.*\)", "", sentido)
                sentido = sentido.replace(linha.nome, "").strip()

            for match in re.finditer(padrao_hora, texto_norm):
                if not match or not sentido or not dia:
                    continue

                horarios.append(
                    [
                        Horario(
                            linha=linha.nome,
                            dia=dia,
                            empresa=self.NOME_EMPRESA,
                            hora=hora,
                            sentido=sentido,
                        )
                        for hora in match.groups()
                    ]
                )

        pp(horarios)
        self.esperar()
        return horarios
