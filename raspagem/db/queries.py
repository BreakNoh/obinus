INSERIR_LINHA = """
    INSERT INTO linhas(empresa, codigo, nome, detalhe, eh_executivo, url) 
    VALUES (
        :empresa,
        :codigo,
        :nome,
        :detalhe,
        :executivo,
        :url
    )
"""

INSERIR_HORARIO = """
    INSERT INTO horarios(empresa, linha, sentido, hora, dia) 
    VALUES (
        :empresa,
        :linha,
        :sentido,
        :hora,
        :dia
    )
"""
