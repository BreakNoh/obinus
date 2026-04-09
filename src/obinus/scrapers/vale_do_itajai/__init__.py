from obinus.scrapers.vale_do_itajai.bcbus import BCBus
from obinus.scrapers.vale_do_itajai.blumob import BluMob
from obinus.scrapers.vale_do_itajai.consorcio_atalaia import ConsorcioAtalaia
from obinus.scrapers.vale_do_itajai.expresso_presidente import (
    ExpressoPresidenteGaspar,
    ExpressoPresidenteRioMafra,
    ExpressoPresidenteTimbo,
)
from obinus.scrapers.vale_do_itajai.nosso_brusque import ConsorcioNossoBrusque
from obinus.scrapers.vale_do_itajai.onibus_circular import OnibusCircular
from obinus.scrapers.vale_do_itajai.viacao_praiana import ViacaoPraiana

RASPADORES_VALE_DO_ITAJAI = {
    "bcbus": BCBus,
    "blumob": BluMob,
    "consorcio_atalaia": ConsorcioAtalaia,
    "expresso_presidente_gaspar": ExpressoPresidenteGaspar,
    "expresso_presidente_rio_mafra": ExpressoPresidenteRioMafra,
    "expresso_presidente_timbo": ExpressoPresidenteTimbo,
    "nosso_brusque": ConsorcioNossoBrusque,
    "onibus_circular": OnibusCircular,
    "viacao_praiana": ViacaoPraiana,
}
