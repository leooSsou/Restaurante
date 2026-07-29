from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.item_comanda import ItemComanda

class ItemComandaRepositoryInterface(ABC):
    @abstractmethod
    def salvar(self, item: ItemComanda) -> ItemComanda:
        """Salva o item de consumo na persistência.
        
        Args:
            item (ItemComanda): Entidade de item de comanda.
            
        Returns:
            ItemComanda: Item persistido.
        """
        pass

    @abstractmethod
    def buscar_por_id(self, item_id: str) -> Optional[ItemComanda]:
        """Busca um item de comanda pelo ID (UUID).
        
        Args:
            item_id (str): ID do item de comanda.
            
        Returns:
            Optional[ItemComanda]: O item encontrado ou None.
        """
        pass
