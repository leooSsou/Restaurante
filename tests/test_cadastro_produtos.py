import pytest
from typing import Optional, List
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.entities.produto import Produto
from src.domain.repositories.produto_repository import ProdutoRepositoryInterface
from src.use_cases.cadastrar_produto import CadastrarProdutoUseCase, CadastrarProdutoInput
from src.use_cases.listar_produtos import ListarProdutosUseCase
from src.adapters.repositories.mysql_produto_repository import MySQLProdutoRepository
from src.infrastructure.database.connection import Base

# --- Fake/Mock Repository para Testes Unitários dos Casos de Uso ---
class FakeProdutoRepository(ProdutoRepositoryInterface):
    def __init__(self):
        self.produtos = []
        self.proximo_id = 1

    def salvar(self, produto: Produto) -> Produto:
        if not produto.id:
            produto.id = self.proximo_id
            self.proximo_id += 1
            self.produtos.append(produto)
        else:
            for idx, p in enumerate(self.produtos):
                if p.id == produto.id:
                    self.produtos[idx] = produto
                    break
        return produto

    def buscar_por_id(self, produto_id: int) -> Optional[Produto]:
        for p in self.produtos:
            if p.id == produto_id:
                return p
        return None

    def buscar_por_codigo_barras(self, codigo_barras: str) -> Optional[Produto]:
        for p in self.produtos:
            if p.codigo_barras == codigo_barras:
                return p
        return None

    def listar_todos(self) -> list[Produto]:
        return list(self.produtos)


# --- Testes Unitários de Regras de Domínio ---
def test_validacao_regras_dominio_produto():
    # Caso 1: Tipo inválido
    with pytest.raises(ValueError, match="tipo do produto deve ser"):
        Produto(nome="Teste", tipo="invalido", ncm="12345678", cfop="5102", icms_csosn="500", pis_cst="01", cofins_cst="01")
        
    # Caso 2: Produto por peso sem preco_por_kg
    with pytest.raises(ValueError, match="devem possuir preco_por_kg"):
        Produto(nome="Buffet", tipo="peso", ncm="12345678", cfop="5102", icms_csosn="500", pis_cst="01", cofins_cst="01")
        
    # Caso 3: NCM inválido (menor que 8)
    with pytest.raises(ValueError, match="NCM deve possuir exatamente 8"):
        Produto(nome="Buffet", tipo="peso", preco_por_kg=60.0, ncm="123", cfop="5102", icms_csosn="500", pis_cst="01", cofins_cst="01")


# --- Testes Unitários de Casos de Uso ---
def test_cadastrar_produto_use_case():
    repo = FakeProdutoRepository()
    use_case = CadastrarProdutoUseCase(repo)
    
    dados = CadastrarProdutoInput(
        nome="Coca-Cola 350ml",
        tipo="unitario",
        codigo_barras="78912345",
        preco_unitario=5.50,
        ncm="22021000",
        cfop="5102",
        icms_csosn="500",
        pis_cst="04",
        cofins_cst="04"
    )
    
    # Act
    produto_criado = use_case.executar(dados)
    
    # Assert
    assert produto_criado.id == 1
    assert produto_criado.nome == "Coca-Cola 350ml"
    
    # Tentar cadastrar duplicado deve levantar ValueError
    with pytest.raises(ValueError, match="já está cadastrado"):
        use_case.executar(dados)


# --- Testes de Integração da Persistência (SQLite) ---
TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture(name="db_session")
def fixture_db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

def test_mysql_repositorio_produto_integracao(db_session):
    repo = MySQLProdutoRepository(db_session)
    
    p = Produto(
        nome="Guaraná 2L",
        tipo="unitario",
        codigo_barras="789000111",
        preco_unitario=8.50,
        ncm="22021000",
        cfop="5102",
        icms_csosn="500",
        pis_cst="04",
        cofins_cst="04"
    )
    
    # Act - Salvar
    repo.salvar(p)
    
    # Assert - Buscar por ID
    p_buscado = repo.buscar_por_id(p.id)
    assert p_buscado is not None
    assert p_buscado.nome == "Guaraná 2L"
    assert p_buscado.preco_unitario == 8.50
    
    # Act - Listar todos
    produtos = repo.listar_todos()
    assert len(produtos) == 1
