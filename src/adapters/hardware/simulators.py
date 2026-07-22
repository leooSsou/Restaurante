from src.domain.hardware.balanca_interface import BalancaInterface

class SimuladorBalancaAdapter(BalancaInterface):
    def __init__(self, peso_padrao_gramas: int = 500):
        self._peso = peso_padrao_gramas

    def definir_peso_simulado(self, peso_gramas: int) -> None:
        """Método auxiliar para alterar o peso durante testes ou simulações."""
        self._peso = peso_gramas

    async def ler_peso_em_gramas(self) -> int:
        return self._peso
