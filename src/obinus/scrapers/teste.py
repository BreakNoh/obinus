import random
from obinus.core.base import Raspador
from obinus.core.modelos import Linha, Horario
from obinus.utils.texto import texto_aleatorio


class Teste(Raspador):
    def empresa(self) -> str:
        return "TESTE"

    def raspar_linhas(self) -> list[Linha]:
        linhas = []

        for _ in range(5):
            linha = Linha(
                empresa=texto_aleatorio(16),
                codigo=texto_aleatorio(5, "0123456789"),
                nome=texto_aleatorio(16),
                detalhe=texto_aleatorio(8),
                executivo=random.random() >= 0.5,
                url=f"https://{texto_aleatorio(10)}.{texto_aleatorio(3)}",
            )

            linhas.append(linha)

        return linhas

    def raspar_horarios_linha(self, linha: Linha) -> list[Horario]:
        horarios = []

        for _ in range(5):
            horario = Horario(
                empresa=linha.empresa,
                linha=linha.codigo,
                sentido=texto_aleatorio(16),
                hora=f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}",
                dia=random.choice(["UTIL", "SABADO", "DOMINGO_FERIADO"]),
            )

            horarios.append(horario)

        return horarios
