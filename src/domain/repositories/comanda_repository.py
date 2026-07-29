from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.comanda import Comanda

class ComandaRepositoryInterface(ABC):
    @abstractmethod
    def salvar(self, comanda: Comanda) -> Comanda:
        """Salva a comanda na persistência e retorna a comanda salva com ID atualizado.
        
        Args:
            comanda (Comanda): Entidade de comanda.
            
        Returns:
            Comanda: Comanda persistida.
        """
        pass

    @abstractmethod
    def buscar_por_id(self, comanda_id: str) -> Optional[Comanda]:
        """Busca uma comanda pelo ID (UUID).
        
        Args:
            comanda_id (str): ID único da comanda.
            
        Returns:
            Optional[Comanda]: A comanda encontrada ou None.
        """
        pass

    @abstractmethod
    def buscar_ativa_por_cartao(self, numero_cartao: str) -> Optional[Comanda]:
        """Busca uma comanda aberta (esta_aberta = True) vinculada ao número do cartão.
        
        Args:
            numero_cartao (str): O número físico do cartão/comanda.
            
        Returns:
            Optional[Comanda]: A comanda aberta ativa ou None se não houver.
        """
        pass
