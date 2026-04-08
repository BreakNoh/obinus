import utils
from obinus.scrapers.sul.grupo_forquilinhas import GrupoForquilhinha

ams_lin, ams_hor = utils.carregar(
    __file__, ["amostra_linhas.html", "amostra_horarios.html"]
)
raspador = GrupoForquilhinha()
