from pydantic import BaseModel, Field
from typing import Optional
from src.domain.entities.produto import Produto
from src.domain.repositories.produto_repository import ProdutoRepositoryInterface

class CadastrarProdutoInput(BaseModel):
    nome: str = Field(..., min_length=2, max_length=150)
    tipo: str = Field(..., description="Deve ser 'peso' ou 'unitario'")
    ncm: str = Field(..., min_length=8, max_length=8)
    cfop: str = Field(..., min_length=4, max_length=4)
    icms_csosn: str = Field(..., min_length=3, max_length=4)
    pis_cst: str = Field(..., min_length=2, max_length=2)
    cofins_cst: str = Field(..., min_length=2, max_length=2)
    codigo_barras: Optional[str] = None
    preco_por_kg: Optional[float] = None
    preco_unitario: Optional[float] = None
    cest: Optional[str] = None

class CadastrarProdutoUseCase:
    def __init__(self, produto_repo: ProdutoRepositoryInterface):
        self.produto_repo = produto_repo

    def executar(self, dados: CadastrarProdutoInput) -> Produto:
        # 1. Validar se o produto com o mesmo código de barras já existe
        if dados.codigo_barras:
            produto_existente = self.produto_repo.buscar_por_codigo_barras(dados.codigo_barras)
            if produto_existente:
                raise ValueError(f"Produto com o código de barras '{dados.codigo_barras}' já está cadastrado")

        # 2. Instanciar a entidade de domínio (ela executará as validações de domínio PEP/fiscais)
        produto = Produto(
            nome=dados.nome,
            tipo=dados.tipo,
            ncm=dados.ncm,
            cfop=dados.cfop,
            icms_csosn=dados.icms_csosn,
            pis_cst=dados.pis_cst,
            cofins_cst=dados.cofins_cst,
            codigo_barras=dados.codigo_barras,
            preco_por_kg=dados.preco_por_kg,
            preco_unitario=dados.preco_unitario,
            cest=dados.cest
        )

        # 3. Salvar na persistência através da interface do repositório
        return self.produto_repo.salvar(produto)
