# Esse daqui tá um merda pq o site é bem ruim de raspar
# o layout não é concistente entre as paginas
# fiz o melhor que conseguir pra raspar o máximo possível
# com a minha paciencia
#
# minha solução foi usar 2 stacks pra simular o fluxo que aparecem no site
# pq a estrutura não tem classes ou ids para diferenciar

import re
from typing import TypedDict
from obinus.core.base import Raspador
from obinus.core.modelos import Linha, Horario
from obinus.utils.http import get_json, get_soup
from obinus.utils.texto import extrair_texto
import pathlib
import jmespath

ARQUIVO_ATUAL = pathlib.Path(__file__)
ARQUIVO_URL = ARQUIVO_ATUAL.parent / "url_santa_cruz.txt"

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


class SantaCruz(Raspador):
    NOME_EMPRESA = "SANTA_CRUZ"

    def raspar_linhas(self) -> list[Linha]:
        url = ""
        try:
            url = open(ARQUIVO_URL, "r").read()
        except Exception as e:
            print(f"X erro ao abrir {ARQUIVO_URL}:", e)
            return []

        linhas = []

        json, status = get_json(url)

        query: list[DadosLinha] = QUERY_LINHAS.search(json)

        if query == [] or query is None:
            return []

        for l in query:
            linha = Linha(
                empresa=self.NOME_EMPRESA,
                codigo="",
                detalhe="",
                nome=l["nome"],
                url=URL_HORARIO % l["endpoint"],
            )
            linhas.append(linha)

        self.esperar()
        return linhas

    def _assinar_papel(self, s: str, ultimo: str) -> str:
        s_norm = s.replace("\n", " ").lower().strip()
        if "segunda" in s_norm or "sexta" in s_norm:
            return "UTIL"
        if "sábado" in s.lower().strip():
            return "SABADO"

        if re.match(r"\d{2}:\d{2}", s_norm):
            if len(s_norm) > 5:
                return "HORARIOS_MULTIPLOS"
            return "HORARIOS"

        if ("saidas" in s_norm or "saídas" in s_norm) and len(s_norm) < 50:
            return "SENTIDO"
        elif ultimo == "SENTIDO":
            return "SENTIDO_CONTINUA"

        return "LIXO"

    def raspar_horarios_linha(self, linha: Linha) -> list[Horario]:
        soup, status = get_soup(linha.url)

        info_que_importa = soup.select("*")
        if info_que_importa is None:
            return []

        stack_info = [
            extrair_texto(tag) for tag in info_que_importa if tag.get_text()
        ]  # Le todas as strings do html

        stack_dias: list[str] = []
        stack_blocos: list[list[Horario]] = []

        horarios = []
        buffer_horarios = []

        ult = ""
        dia = ""
        sentido = ""

        for info in stack_info:
            papel = self._assinar_papel(
                info, ult
            )  # Assina um token com seu papel no fluxo, é baseado numa logica que inventei

            if papel == "LIXO":
                continue

            ult = papel

            match papel:
                case "UTIL" | "SABADO":
                    # guarda os dias num stack para depois botar nos horarios
                    # faz isso pq o fluxo do site é: cabecalho, cabecalho, horaios...

                    stack_dias.append(papel)
                case "SENTIDO":
                    sentido = info
                    if len(buffer_horarios) > 0:
                        stack_blocos.append(buffer_horarios)
                        buffer_horarios = []

                case "SENTIDO_CONTINUA":
                    # concatena o resto do sentido, alguns veem separados em tags irmas
                    sentido += " " + info

                case "HORARIOS_MULTIPLOS":
                    # horarios as vezes ocupam a mesma tag
                    for hora in info.split(" "):
                        buffer_horarios.append(
                            Horario(
                                dia="",
                                empresa=self.NOME_EMPRESA,
                                sentido=sentido.strip(),
                                linha=linha.nome,
                                hora=hora,
                            )
                        )

                case "HORARIOS":
                    buffer_horarios.append(
                        Horario(
                            dia="",
                            empresa=self.NOME_EMPRESA,
                            sentido=sentido.strip(),
                            linha=linha.nome,
                            hora=info,
                        )
                    )

        if len(buffer_horarios) > 0:
            stack_blocos.append(buffer_horarios)

        if len(stack_dias) == len(stack_blocos):
            # se o numero do dia e blocos de horario forem o mesmo
            # provavelmete é uma coluna dias uteis e uma sábado

            while len(stack_dias) > 0:
                dia = stack_dias.pop()

                for h in stack_blocos.pop():
                    h.dia = dia
                    horarios.append(h)

        elif len(stack_dias) == 1:
            # se só tem um dia, todos os horarios são pra ele
            dia = stack_dias.pop(0)

            for b in stack_blocos:
                for h in b:
                    h.dia = dia

        elif len(stack_blocos) > len(stack_dias):
            # se o numero de blocos de horarios for maior que o num de dias
            # assinar 2 colunas pegando do inicio dos 2 stacks

            contagem = 0
            dia = stack_dias.pop(0)

            while len(stack_blocos) > 0:
                if contagem >= 2:
                    dia = stack_dias.pop(0)
                    contagem = 0

                bloco = stack_blocos.pop(0)
                for h in bloco:
                    h.dia = dia
                    horarios.append(h)

                contagem += 1

        # pprint.pp(horarios)
        self.esperar()
        return horarios
