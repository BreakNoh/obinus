from common import Raspador, Linha, Horario


class Teste(Raspador):
    def empresa(self) -> str:
        return "TESTE"

    def raspar_linhas(self) -> list[Linha]:
        return [
            Linha(
                "SPEEDWAGON_FOUNDATION",
                "P3-EGY",
                "STARDUST_CRUSADERS",
                "VIA_EGITO",
                True,
                "https://spw.com/p3",
            ),
            Linha(
                "SPEEDWAGON_FOUNDATION",
                "P4-MOR",
                "DIAMOND_IS_UNBREAKABLE",
                "VIA_MORIOH",
                False,
                "https://spw.com/p4",
            ),
            Linha(
                "SPEEDWAGON_FOUNDATION",
                "P5-ITA",
                "GOLDEN_WIND",
                "VIA_ITALIA",
                True,
                "https://spw.com/p5",
            ),
        ]

    def raspar_horarios_linha(self, linha: Linha) -> list[Horario]:
        if "P3-EGY" in linha.codigo:
            return [
                Horario(linha.empresa, linha.codigo, "IDA", "06:00", "UTIL"),
                Horario(linha.empresa, linha.codigo, "IDA", "12:00", "UTIL"),
                Horario(linha.empresa, linha.codigo, "IDA", "18:00", "UTIL"),
                Horario(linha.empresa, linha.codigo, "VOLTA", "09:00", "SABADO"),
                Horario(
                    linha.empresa, linha.codigo, "VOLTA", "21:00", "DOMINGO_FERIADO"
                ),
            ]

        elif "P4-MOR" in linha.codigo:
            return [
                Horario(linha.empresa, linha.codigo, "CIRCULAR", "07:15", "UTIL"),
                Horario(linha.empresa, linha.codigo, "CIRCULAR", "08:45", "UTIL"),
                Horario(linha.empresa, linha.codigo, "CIRCULAR", "12:30", "UTIL"),
                Horario(linha.empresa, linha.codigo, "CIRCULAR", "17:00", "UTIL"),
                Horario(
                    linha.empresa, linha.codigo, "CIRCULAR", "23:59", "SABADO"
                ),  # Horário do terror
            ]

        elif "P5-ITA" in linha.codigo:
            return [
                Horario(linha.empresa, linha.codigo, "IDA", "05:30", "UTIL"),
                Horario(linha.empresa, linha.codigo, "IDA", "10:00", "UTIL"),
                Horario(linha.empresa, linha.codigo, "VOLTA", "15:20", "UTIL"),
                Horario(linha.empresa, linha.codigo, "VOLTA", "19:40", "UTIL"),
                Horario(linha.empresa, linha.codigo, "IDA", "08:00", "DOMINGO_FERIADO"),
            ]

        return []
