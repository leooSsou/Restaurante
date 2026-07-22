from typing import List
from src.domain.entities.produto import Produto
from src.domain.repositories.produto_repository import ProdutoRepositoryInterface

class ListarProdutosUseCase:
    def __init__(self, produto_repo: ProdutoRepositoryInterface):
        self.produto_repo = produto_repo

    def executar(self) -> List[Produto]:
        return self.produto_repo.listar_todos()
