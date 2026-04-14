import re
from typing import cast
from bs4 import BeautifulSoup
from obinus.utils.http import extrair_texto, get_json, get_soup
from obinus.core import *
from pathlib import Path
from obinus.utils.http import HEADERS_BASE, get_soup
import pprint


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

            linhas.append((Linha(nome), Raw(str(codigo))))

        return linhas

    def buscar_horarios(self, busca: Raw) -> Html:
        payload = PAYLOAD_TEMPLATE % busca.valor
        headers = HEADERS_BASE | {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://praiana.com.br/horarios/",
        }

        json = cast(
            dict, get_json(URL_HORARIOS, data=payload, headers=headers, metodo="POST")
        )

        html = BeautifulSoup(json["content"], "html.parser")

        return Html(html)

    def normalizar_dia(self, d: str) -> Dias:
        d_norm = d.lower().strip()

        if d_norm == "":
            return DIAS_UTEIS

        dias = 0

        if "sex" in d_norm and "seg" in d_norm:
            dias |= DIAS_UTEIS

        if "sáb" in d_norm or "sab" in d_norm:
            dias |= SABADO

        if "feri" in d_norm and "domi" in d_norm:
            dias |= DOMINGO_E_FERIADOS

        return dias if dias > 0 else DIAS_UTEIS

    def extrair_horarios(self, payload: Html) -> list[Servico]:
        SELETOR_BLOCO = "div.jet-equal-columns[data-post-id]"
        SELETOR_SENTIDO = "div.jet-listing-dynamic-field__content"
        SELETOR_HORARIOS = "span.elementor-icon-list-text"
        PADRAO_SENTIDO_DIA = re.compile(r"(?P<sent>[^\(\)]+)(?P<dia>\(.+\))?")
        PADRAO_HORA = re.compile(r"\d{2}:\d{2}")

        servicos = []

        for bloco in payload.html.select(SELETOR_BLOCO):
            servico = None

            for i in bloco.select(SELETOR_SENTIDO):
                if not (texto := extrair_texto(i)):
                    # texto não extraido ou inválido (tarifa ou vazio)
                    continue

                if texto == "" or "$" in texto:
                    continue

                if match := PADRAO_SENTIDO_DIA.search(texto):
                    sentido = match.group("sent").strip()
                    dia = match.group("dia")

                    dias = self.normalizar_dia(dia) if dia else DIAS_UTEIS

                    servico = Servico(dias, sentido)
                    break
            else:
                continue

            print(servico)
            for i in bloco.select(SELETOR_HORARIOS):
                if not (texto := extrair_texto(i)):
                    continue

                for h in PADRAO_HORA.findall(texto):
                    servico.horarios.append(Horario(h))

            servicos.append(servico)

        return servicos
