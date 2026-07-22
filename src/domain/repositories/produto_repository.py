from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.produto import Produto

class ProdutoRepositoryInterface(ABC):
    @abstractmethod
    def salvar(self, produto: Produto) -> Produto:
        """Salva um produto na persistência e retorna o produto salvo com seu ID.
        
        Args:
            produto (Produto): Entidade de domínio do produto.
            
        Returns:
            Produto: O produto salvo com ID preenchido.
        """
        pass

    @abstractmethod
    def buscar_por_id(self, produto_id: int) -> Optional[Produto]:
        """Busca um produto pelo ID.
        
        Args:
            produto_id (int): ID do produto.
            
        Returns:
            Optional[Produto]: O produto encontrado ou None.
        """
        pass

    @abstractmethod
    def buscar_por_codigo_barras(self, codigo_barras: str) -> Optional[Produto]:
        """Busca um produto pelo código de barras.
        
        Args:
            codigo_barras (str): Código de barras.
            
        Returns:
            Optional[Produto]: O produto encontrado ou None.
        """
        pass

    @abstractmethod
    def listar_todos(self) -> List[Produto]:
        """Lista todos os produtos cadastrados.
        
        Returns:
            List[Produto]: Lista contendo todos os produtos.
        """
        pass
