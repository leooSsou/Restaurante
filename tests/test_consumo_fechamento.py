import pytest
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.entities.comanda import Comanda
from src.domain.entities.produto import Produto
from src.domain.entities.item_comanda import ItemComanda
from src.domain.entities.pagamento import Pagamento

from src.domain.repositories.comanda_repository import ComandaRepositoryInterface
from src.domain.repositories.produto_repository import ProdutoRepositoryInterface
from src.domain.repositories.item_comanda_repository import ItemComandaRepositoryInterface

from src.use_cases.lancar_item_comanda import LancarItemComandaUseCase, LancarItemComandaInput
from src.use_cases.fechar_comanda import FecharComandaUseCase, FecharComandaInput

from src.adapters.repositories.mysql_comanda_repository import MySQLComandaRepository
from src.adapters.repositories.mysql_produto_repository import MySQLProdutoRepository
from src.adapters.repositories.mysql_item_comanda_repository import MySQLItemComandaRepository
from src.infrastructure.database.connection import Base


# --- Fakes para Testes Unitários ---
class FakeComandaRepository(ComandaRepositoryInterface):
    def __init__(self):
        self.comandas = []

    def salvar(self, comanda: Comanda) -> Comanda:
        for idx, c in enumerate(self.comandas):
            if c.id == comanda.id:
                self.comandas[idx] = comanda
                return comanda
        self.comandas.append(comanda)
        return comanda

    def buscar_por_id(self, comanda_id: str) -> Optional[Comanda]:
        for c in self.comandas:
            if c.id == comanda_id:
                return c
        return None

    def buscar_ativa_por_cartao(self, numero_cartao: str) -> Optional[Comanda]:
        for c in self.comandas:
            if c.numero_cartao == numero_cartao and c.esta_aberta:
                return c
        return None


class FakeProdutoRepository(ProdutoRepositoryInterface):
    def __init__(self):
        self.produtos = []

    def salvar(self, produto: Produto) -> Produto:
        self.produtos.append(produto)
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

    def listar_todos(self) -> List[Produto]:
        return list(self.produtos)


class FakeItemComandaRepository(ItemComandaRepositoryInterface):
    def __init__(self):
        self.itens = []

    def salvar(self, item: ItemComanda) -> ItemComanda:
        self.itens.append(item)
        return item

    def buscar_por_id(self, item_id: str) -> Optional[ItemComanda]:
        for i in self.itens:
            if i.id == item_id:
                return i
        return None


# --- Testes Unitários do Lançamento de Consumo ---
def test_lancar_item_comanda_peso_sucesso():
    comanda_repo = FakeComandaRepository()
    produto_repo = FakeProdutoRepository()
    item_repo = FakeItemComandaRepository()
    
    comanda = Comanda(id="c-1", numero_cartao="10")
    comanda_repo.salvar(comanda)
    
    produto = Produto(id=1, nome="Buffet/Kg", tipo="peso", preco_por_kg=60.0, ncm="21069090", cfop="5101", icms_csosn="102", pis_cst="01", cofins_cst="01")
    produto_repo.salvar(produto)
    
    use_case = LancarItemComandaUseCase(comanda_repo, produto_repo, item_repo)
    dados = LancarItemComandaInput(comanda_id="c-1", produto_id=1, quantidade=0.450)  # 450g
    
    # Act
    item = use_case.executar(dados)
    
    # Assert
    assert item.preco_total == 27.00  # 0.45 * 60.0


def test_lancar_item_comanda_unitario_erro_quantidade_decimal():
    comanda_repo = FakeComandaRepository()
    produto_repo = FakeProdutoRepository()
    item_repo = FakeItemComandaRepository()
    
    comanda = Comanda(id="c-1", numero_cartao="10")
    comanda_repo.salvar(comanda)
    
    produto = Produto(id=2, nome="Suco lata", tipo="unitario", preco_unitario=6.0, ncm="22021000", cfop="5102", icms_csosn="500", pis_cst="04", cofins_cst="04")
    produto_repo.salvar(produto)
    
    use_case = LancarItemComandaUseCase(comanda_repo, produto_repo, item_repo)
    dados = LancarItemComandaInput(comanda_id="c-1", produto_id=2, quantidade=1.5)  # Quantidade fracionária
    
    # Act & Assert
    with pytest.raises(ValueError, match="deve ser um número inteiro"):
        use_case.executar(dados)


# --- Testes Unitários de Fechamento de Comanda ---
def test_fechar_comanda_sucesso_saldo_zerado():
    comanda_repo = FakeComandaRepository()
    use_case = FecharComandaUseCase(comanda_repo)
    
    comanda = Comanda(id="c-1", numero_cartao="10")
    # Comanda sem itens e sem pagamentos tem saldo zero
    comanda_repo.salvar(comanda)
    
    # Act
    comanda_fechada = use_case.executar(FecharComandaInput(comanda_id="c-1"))
    
    # Assert
    assert comanda_fechada.esta_aberta is False
    assert comanda_fechada.fechado_em is not None


def test_fechar_comanda_erro_saldo_devedor():
    comanda_repo = FakeComandaRepository()
    use_case = FecharComandaUseCase(comanda_repo)
    
    comanda = Comanda(id="c-1", numero_cartao="10")
    item = ItemComanda(id="i-1", comanda_id="c-1", produto_id=1, quantidade=1.0, preco_unitario=15.0, preco_total=15.0)
    comanda.adicionar_item(item)
    # Comanda com consumo de R$ 15,00 e sem pagamentos
    comanda_repo.salvar(comanda)
    
    # Act & Assert
    with pytest.raises(ValueError, match="Saldo devedor restante: R\\$ 15.00"):
        use_case.executar(FecharComandaInput(comanda_id="c-1"))


def test_fechar_comanda_sucesso_com_pagamento():
    comanda_repo = FakeComandaRepository()
    use_case = FecharComandaUseCase(comanda_repo)
    
    comanda = Comanda(id="c-1", numero_cartao="10")
    item = ItemComanda(id="i-1", comanda_id="c-1", produto_id=1, quantidade=1.0, preco_unitario=15.0, preco_total=15.0)
    comanda.adicionar_item(item)
    
    pagamento = Pagamento(comanda_id="c-1", valor=15.00, metodo_pagamento="pix")
    comanda.registrar_pagamento(pagamento)
    
    comanda_repo.salvar(comanda)
    
    # Act
    comanda_fechada = use_case.executar(FecharComandaInput(comanda_id="c-1"))
    
    # Assert
    assert comanda_fechada.esta_aberta is False


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

def test_mysql_repositorios_consumo_fechamento_integracao(db_session):
    comanda_repo = MySQLComandaRepository(db_session)
    produto_repo = MySQLProdutoRepository(db_session)
    item_repo = MySQLItemComandaRepository(db_session)
    
    # 1. Salvar Produto
    produto = Produto(
        nome="Guaraná 350ml",
        tipo="unitario",
        preco_unitario=5.00,
        ncm="22021000",
        cfop="5102",
        icms_csosn="500",
        pis_cst="04",
        cofins_cst="04"
    )
    produto_repo.salvar(produto)
    
    # 2. Abrir Comanda
    comanda = Comanda(
        id="comanda-uuid-999",
        numero_cartao="00999",
        esta_aberta=True,
        criado_em=datetime.now()
    )
    comanda_repo.salvar(comanda)
    
    # 3. Lançar item consumido
    item = ItemComanda(
        id="item-uuid-999",
        comanda_id=comanda.id,
        produto_id=produto.id,
        quantidade=2.0,
        preco_unitario=produto.preco_unitario,
        preco_total=10.00
    )
    item_repo.salvar(item)
    
    # 4. Validar carregamento do consumo ao buscar comanda
    comanda_carregada = comanda_repo.buscar_por_id("comanda-uuid-999")
    assert comanda_carregada is not None
    assert len(comanda_carregada.itens) == 1
    assert comanda_carregada.itens[0].preco_total == 10.00
    assert comanda_carregada.obter_valor_total() == 10.00
