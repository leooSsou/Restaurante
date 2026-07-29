import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from src.domain.entities.item_comanda import ItemComanda
from src.domain.repositories.comanda_repository import ComandaRepositoryInterface
from src.domain.repositories.produto_repository import ProdutoRepositoryInterface
from src.domain.repositories.item_comanda_repository import ItemComandaRepositoryInterface

class LancarItemComandaInput(BaseModel):
    comanda_id: str = Field(..., description="ID único da comanda")
    produto_id: int = Field(..., description="ID único do produto")
    quantidade: float = Field(..., description="Quantidade (peso em kg ou unidades)")

class LancarItemComandaUseCase:
    def __init__(
        self,
        comanda_repo: ComandaRepositoryInterface,
        produto_repo: ProdutoRepositoryInterface,
        item_repo: ItemComandaRepositoryInterface
    ):
        self.comanda_repo = comanda_repo
        self.produto_repo = produto_repo
        self.item_repo = item_repo

    def executar(self, dados: LancarItemComandaInput) -> ItemComanda:
        # 1. Buscar e validar comanda
        comanda = self.comanda_repo.buscar_por_id(dados.comanda_id)
        if not comanda:
            raise ValueError(f"Comanda com ID '{dados.comanda_id}' não encontrada")
        if not comanda.esta_aberta:
            raise ValueError("Não é possível registrar itens de consumo em uma comanda fechada")

        # 2. Buscar e validar produto
        produto = self.produto_repo.buscar_por_id(dados.produto_id)
        if not produto:
            raise ValueError(f"Produto com ID '{dados.produto_id}' não encontrado")

        # 3. Validar quantidade e definir preço conforme o tipo
        preco_unitario = 0.0
        if produto.tipo == "peso":
            if produto.preco_por_kg is None:
                raise ValueError("Produto do tipo 'peso' não possui preço por Kg configurado")
            preco_unitario = produto.preco_por_kg
        elif produto.tipo == "unitario":
            if produto.preco_unitario is None:
                raise ValueError("Produto do tipo 'unitario' não possui preço unitário configurado")
            
            # Garante que produtos unitários tenham quantidades inteiras
            if not dados.quantidade.is_integer():
                raise ValueError(f"Quantidade para o produto '{produto.nome}' (unitário) deve ser um número inteiro")
            
            preco_unitario = produto.preco_unitario

        # 4. Criar a entidade de domínio do item (calcula preco_total de forma precisa)
        item = ItemComanda(
            id=str(uuid.uuid4()),
            comanda_id=comanda.id,
            produto_id=produto.id,
            quantidade=dados.quantidade,
            preco_unitario=preco_unitario,
            criado_em=datetime.now()
        )

        # 5. Persistir e retornar
        return self.item_repo.salvar(item)
