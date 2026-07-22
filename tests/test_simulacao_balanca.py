import pytest
from src.domain.entities.comanda import Comanda
from src.adapters.hardware.simulators import SimuladorBalancaAdapter

from src.domain.entities.item_comanda import ItemComanda

def test_calculo_preco_comanda():
    # Arrange
    comanda = Comanda(id="1", numero_cartao="100")
    # Item por quilo: 750 gramas = 0.750 kg
    item = ItemComanda(
        comanda_id=comanda.id,
        produto_id=999,
        quantidade=0.750,
        preco_unitario=59.90
    )

    # Act
    comanda.adicionar_item(item)

    # Assert
    assert comanda.obter_valor_total() == 44.93

@pytest.mark.asyncio
async def test_leitura_balanca_simulada():
    # Arrange
    balanca = SimuladorBalancaAdapter(peso_padrao_gramas=500)

    # Act
    peso_inicial = await balanca.ler_peso_em_gramas()
    
    balanca.definir_peso_simulado(820)
    peso_atualizado = await balanca.ler_peso_em_gramas()

    # Assert
    assert peso_inicial == 500
    assert peso_atualizado == 820
