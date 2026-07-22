from abc import ABC, abstractmethod

class BalancaInterface(ABC):
    @abstractmethod
    async def ler_peso_em_gramas(self) -> int:
        """Lê o peso atual da balança física ou simulada e retorna o valor em gramas.
        
        Returns:
            int: Peso lido em gramas.
        """
        pass
