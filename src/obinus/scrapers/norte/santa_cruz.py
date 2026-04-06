# Aqui eu fiz arte

import re
from typing import TypedDict, cast
from bs4 import BeautifulSoup, Tag
from obinus.core.raspador import InterfaceRaspador
from obinus.core.tipos import *
from obinus.utils.http import get_json, get_soup
from obinus.utils.texto import extrair_texto
import pathlib
import jmespath

ARQUIVO_URL = pathlib.Path(__file__).parent / "url_santa_cruz.txt"
URL_HORARIO = "https://www.coletivosantacruz.com.br/%s"


class DadosLinha(TypedDict):
    nome: str
    endpoint: str


QUERY_LINHAS = jmespath.compile("""
    props.siteWixCodeSdk.nonPopupsPagesData[].{
        nome: title,
        endpoint: pageFullPath
    }
""")


class Tratador:
    def criar_sentido(self, idx_dia: int, nome: str, alvo: BeautifulSoup) -> Tag:
        ORDEM_DIAS = ["DU", "SAB", "DOM"]

        sentido = alvo.new_tag("ul")
        sentido["class"] = "col-sentido"
        sentido["data-sentido"] = nome
        sentido["data-dia"] = ORDEM_DIAS[idx_dia]

        alvo.append(sentido)

        return sentido

    def tratar_sentidos(self, html: BeautifulSoup | Tag, alvo: BeautifulSoup):
        SELETOR_ITENS = "p.font_8.wixui-rich-text__text"
        SELETOR_TEXTO = "span.wixui-rich-text__text[style*='26px'], span"
        PADRAO_HORARIO = re.compile(r"\d{2}:\d{2}")
        PADRAO_INLINE = re.compile(r"[^\d:]+")

        buffer_sentido = ""
        ultimo_alinhamento = "esq"

        idx_dia = 0
        sentido = None
        ultimo_era_bloco = False

        for item in html.select(SELETOR_ITENS):
            if not (filho_texto := item.select_one(SELETOR_TEXTO)):
                continue

            while (sub_filho := filho_texto.select_one(SELETOR_TEXTO)) and sub_filho:
                filho_texto = sub_filho

            texto = extrair_texto(filho_texto).strip().replace("\u200b", "")
            vazia = len(texto) == 0

            if vazia:
                if sentido:  # celula vazia no após horários
                    sentido = None

                elif buffer_sentido != "":  # celula vazia após nome do sentido
                    sentido = self.criar_sentido(idx_dia, buffer_sentido, alvo)
                    buffer_sentido = ""

                continue

            if estilo := item.get("style"):
                alinhamento = "dir" if re.search(r"right", str(estilo)) else "esq"
            else:
                alinhamento = "esq"

            if alinhamento != ultimo_alinhamento or (
                alinhamento == "esq" and ultimo_era_bloco
            ):
                idx_dia = (
                    (idx_dia + 1) % 3 if alinhamento == "esq" else idx_dia
                )  # vai para o próximo dia se alinhamento voltar a ser esquerda
                ultimo_alinhamento = alinhamento

            capturas = list(PADRAO_HORARIO.finditer(texto))
            ultimo_era_bloco = len(capturas) > 1

            for captura in capturas:
                item_horario = alvo.new_tag("li", string=captura.group())
                item_horario["class"] = "item-hora"

                if not sentido:
                    if buffer_sentido != "":
                        sentido = self.criar_sentido(idx_dia, buffer_sentido, alvo)
                        sentido.append(item_horario)
                        buffer_sentido = ""

class SantaCruz(InterfaceRaspador[Json, Html, Url]):
    def empresa(self) -> Empresa: ...

    def buscar_linhas(self) -> Json:
        with open(ARQUIVO_URL, "r") as a:
            url = a.read()
            json = QUERY_LINHAS.search(get_json(url))
            json_final = []

            for i in cast(list[DadosLinha], json):
                if (
                    not i["nome"].isupper() or "-" in i["endpoint"]
                ):  # filtra as paginas que não são linhas
                    json_final.append(i)

            return Json(json_final)

    def buscar_horarios(self, busca: Url) -> Html:
        html_raw = get_soup(busca.url)
        return Html(Tratador().tratar_payload_horarios(html_raw))

    def extrair_horarios(self, payload: Html) -> list[Servico]:
        servicos = []
        DIAS = {"DU": DIAS_UTEIS, "SAB": SABADO, "DOM": DOMINGO_E_FERIADOS}

        for ser in payload.html.select("ul.col-sentido[data-sentido][data-dia]"):
            dias = DIAS[str(ser["data-dia"]).upper()]
            sentido = str(ser["data-sentido"])

            servico = Servico(dias, sentido)

            for item in ser.select("li.item-hora"):
                servico.horarios.append(Horario(extrair_texto(item)))

            servicos.append(servico)

        return servicos

    def extrair_linhas(self, payload: Json) -> list[tuple[Linha, Url]]:
        linhas = []

        if not (json := cast(list[DadosLinha], payload.json)):
            return []

        for lin in json:
            linhas.append((Linha(lin["nome"]), Url(URL_HORARIO % lin["endpoint"])))

        return linhas
