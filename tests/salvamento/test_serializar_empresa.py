from obinus.utils.salvar import gerar_rows
from obinus.core.tipos import *


def test_serializar_empresa():
    mock = Empresa(
        "0",
        "empresa",
        linhas=[
            Linha(
                "linha",
                "1",
                id="12",
                servicos=[
                    Servico(
                        DIAS_UTEIS,
                        "sentido",
                        [Horario("12:34", id="2"), Horario("11:11", id="4")],
                        id="3",
                    )
                ],
            )
        ],
    )

    rows = gerar_rows(mock)

    assert rows["linhas"]
    assert rows["horarios"]
    assert rows["servicos"]
    assert len(rows["linhas"]) == 1
    assert len(rows["servicos"]) == 1
    assert len(rows["horarios"]) == 2
