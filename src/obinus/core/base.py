from .modelos import Linha, Horario
from abc import ABC, abstractmethod


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

    def raspar(self) -> tuple[list[Linha], list[Horario]]:
        print(f"# raspando {self.empresa()}...")

        linhas_raspadas: list[Linha] = self.raspar_linhas()

        print(f"> {len(linhas_raspadas)} linhas raspadas")

        num_horarios = 0

        todos_horarios_raspados = []

        print(f"# raspando horarios...")

        for i, linha in enumerate(linhas_raspadas):
            print(f"> {i + 1}/{len(linhas_raspadas)} linhas raspadas", end="\r")

            horarios_raspados = self.raspar_horarios_linha(linha)
            num_horarios += len(horarios_raspados)

            todos_horarios_raspados.extend(horarios_raspados)

        print(f"> {num_horarios} horarios raspados")

        return linhas_raspadas, todos_horarios_raspados
