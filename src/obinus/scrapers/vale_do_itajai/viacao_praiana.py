import re
from typing import cast
from bs4 import BeautifulSoup
from obinus.utils.http import extrair_texto, get_json, get_soup
from obinus.core import *
from pathlib import Path

from obinus.utils.texto import normalizar_dia

URL_HORARIOS = "https://praiana.com.br/wp-admin/admin-ajax.php"
URL_LINHAS = "https://praiana.com.br/horarios/"
ARQUIVO_BODY = Path(__file__).parent / "body_praiana.txt"
ARQUIVO_BODY_RAW = Path(__file__).parent / "body_praiana_raw.txt"

with open(ARQUIVO_BODY, "r") as a:
    PAYLOAD_TEMPLATE = a.read().replace("\n", "&")


class ViacaoPraiana(InterfaceRaspador[Html, Html, Raw]):
    def empresa(self) -> Empresa:
        return Empresa(
            id="viacao-praiana", nome="Viação Praiana", regioes=VALE_DO_ITAJAI
        )

    def buscar_linhas(self) -> Html:
        return Html(get_soup(URL_LINHAS))

    def extrair_linhas(self, payload: Html) -> list[tuple[Linha, Raw]]:
        linhas = []

        for opt in payload.html.select("select[name='linhas'] option[value!='']"):
            if not (nome := extrair_texto(opt)):
                continue
            if codigo := opt.get("value"):
                if not codigo:
                    continue

            linhas.append((Linha(nome), Raw(f"{codigo}:{nome}")))

        return linhas

    def buscar_horarios(self, busca: Raw) -> Html:
        SELETOR_BLOCO = "div[data-post-id]"
        cod, nome = busca.valor.split(":", maxsplit=1)

        payload = PAYLOAD_TEMPLATE % cod
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://praiana.com.br/horarios/",
        }

        json = cast(
            dict, get_json(URL_HORARIOS, data=payload, headers=headers, metodo="POST")
        )

        html = BeautifulSoup(json["content"], "html.parser")

        for i in html.select(SELETOR_BLOCO):
            if nome:
                i["data-nome-linha"] = nome

        return Html(html)

    def extrair_horarios(self, payload: Html) -> list[Servico]:
        SELETOR_BLOCO = "div[data-post-id]"
        SELETOR_SENTIDO = "div.jet-listing-dynamic-field__content"
        SELETOR_HORARIOS = "span.elementor-icon-list-text"

        PADRAO_SENTIDO_DIA = re.compile(r"(?P<sent>[^\(\)]+)(?P<dia>\(.+\))?")
        PADRAO_HORA = re.compile(r"\d{1,2}:\d{1,2}")

        servicos = []

        for bloco in payload.html.select(SELETOR_BLOCO):
            servico = None
            nome_linha = bloco.get("data-nome-linha")

            for i in bloco.select(SELETOR_SENTIDO):
                if not (texto := extrair_texto(i)):
                    # texto não extraido ou inválido (tarifa ou vazio)
                    continue

                if texto == "" or "$" in texto:
                    continue

                if match := PADRAO_SENTIDO_DIA.search(texto):
                    sentido = match.group("sent").strip()

                    if nome_linha:
                        sentido = sentido.replace(str(nome_linha), "")

                    dia = match.group("dia") or "dia util"

                    dias = normalizar_dia(dia)
                    servico = Servico(dias, sentido)

                    break
            else:
                continue

            for i in bloco.select(SELETOR_HORARIOS):
                if not (texto := extrair_texto(i)):
                    continue

                for h in PADRAO_HORA.findall(texto):
                    servico.horarios.append(Horario(h))

            servicos.append(servico)

        return servicos
