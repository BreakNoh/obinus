import re
from obinus.core import Raspador, Linha, Horario
from obinus.utils import get_soup, extrair_texto

URL_LINHAS = "https://transullages.com.br/linhas"

SELETOR_LINHAS = "table > tr"
SELETOR_NOME = "td:first-child > a"
SELETOR_CODIGO = "td:nth-child(2)"

# SELETOR_DIA = '[role="tablist"]'
SELETOR_DIA_UTIL = '[id="home-tab-pane"] .row > .col'
SELETOR_DIA_SAB = '[id="profile-tab-pane"] .row > .col'
SELETOR_DIA_DOM = '[id="contact-tab-pane"] .row > .col'
SELETOR_SENTIDO = "h6"
SELETOR_HORARIOS = "h6 + div"  # horarios vem num bloco só


class Transul(Raspador):
    NOME_EMPRESA = "TRANSUL"

    def raspar_linhas(self) -> list[Linha]:
        soup, _ = get_soup(URL_LINHAS)
        linhas = []
        print(soup.prettify())

        for lin in soup.select(SELETOR_LINHAS):
            print(lin.prettify())
            nome = extrair_texto(lin.select_one(SELETOR_NOME))
            codigo = extrair_texto(lin.select_one(SELETOR_CODIGO))
            url: str | None = None

            if tag := lin.select_one(SELETOR_NOME):
                url = str(tag.get("href"))

            if not nome or not codigo:
                continue

            linhas.append(
                Linha(
                    empresa=self.NOME_EMPRESA, codigo=codigo, nome=nome, url=url or ""
                )
            )

        return linhas

    def raspar_horarios_linha(self, linha: Linha) -> list[Horario]:
        if linha.url == "":
            return []
        soup, _ = get_soup(linha.url)

        dia_seletor: list[tuple[str, str]] = [
            ("UTIL", SELETOR_DIA_UTIL),
            ("SABADO", SELETOR_DIA_SAB),
            ("DOMINGO_FERIADO", SELETOR_DIA_DOM),
        ]
        horarios = []

        for dia, seletor in dia_seletor:
            for col in soup.select(seletor):
                sentido = extrair_texto(col.select_one(SELETOR_SENTIDO))
                horas = extrair_texto(col.select_one(SELETOR_HORARIOS))

                if not sentido or not horas:
                    continue

                padrao = r"[0-9]{2}:[0-9]{2}"

                for hora in re.findall(padrao, horas):
                    if hora:
                        horarios.append(
                            Horario(
                                empresa=self.NOME_EMPRESA,
                                linha=linha.codigo,
                                sentido=sentido,
                                hora=hora,
                                dia=dia,
                            )
                        )

        self.esperar()
        return horarios
