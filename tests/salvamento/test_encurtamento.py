from obinus.utils.texto import encurtar


def test_encurtar():
    exemplo = "linha 123 via abcdefghj hospital para até florianópolis"
    encurtado = encurtar(exemplo)

    assert encurtado
    assert encurtado == "lin 123 v abcd hosp fpolis"
