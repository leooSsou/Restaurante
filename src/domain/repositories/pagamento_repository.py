from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.pagamento import Pagamento

class PagamentoRepositoryInterface(ABC):
    @abstractmethod
    def salvar(self, pagamento: Pagamento) -> Pagamento:
        """Salva o pagamento na persistência e retorna o pagamento salvo.
        
        Args:
            pagamento (Pagamento): Entidade de pagamento.
            
        Returns:
            Pagamento: Pagamento persistido.
        """
        pass
